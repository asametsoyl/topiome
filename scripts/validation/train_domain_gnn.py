"""Train and evaluate the breast spatial-domain GNN (patient-level split).

Protocol
1. Inner leave-one-patient-out CV over the 4 TRAIN patients picks the number
   of epochs (GNN and the no-graph MLP ablation separately). For every fold the
   scRNA reference and gene panel are rebuilt without the validation patient
   and without the TEST patients.
2. Temperature scaling is fitted on the out-of-fold logits of step 1.
3. The final model is trained on all TRAIN patients and evaluated once on the
   TEST patients, next to three baselines: the no-graph MLP, Topiome's
   k-means + marker labelling, and "always tumor".

Writes the model (NumPy weights + model card) to packages/disease-packs/models
and a report to docs/validation/breast-wu2021.md.

Usage (from apps/api, PyTorch only for training):
    uv run --with torch python -I ../../scripts/validation/train_domain_gnn.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import adjusted_rand_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis import load_visium, run_pipeline  # noqa: E402
from analysis.communication import spatial_graph  # noqa: E402
from analysis.deconvolution import nnls_deconvolve  # noqa: E402
from analysis.gnn import build_features, expected_calibration_error, forward  # noqa: E402
from analysis.qc import normalize_counts, run_qc  # noqa: E402
from wu2021_common import (  # noqa: E402
    CLASSES,
    PACKS,
    ROOT,
    TEST_PATIENTS,
    TRAIN_PATIENTS,
    VISIUM_DIR,
    VISIUM_PATIENTS,
    label_array,
    load_labels,
    marker_panel,
    reference_from_sums,
)

from app.disease_packs import get_pack  # noqa: E402
from app.services.pipeline import pack_genes  # noqa: E402

VERSION = "1.0.0"
MODEL_NAME = "breast_domain_gnn_v1"
EPOCH_GRID = [25, 50, 100, 150, 200, 300]
HIDDEN, DROPOUT, LR, WEIGHT_DECAY, K, SEED = 64, 0.3, 5e-3, 5e-4, 6, 7

torch.set_num_threads(max(1, torch.get_num_threads()))


# ── Data ─────────────────────────────────────────────────────────────────────


def fold_reference(exclude: list[str], pack_markers: list[str]):
    means, detection, cells = reference_from_sums(exclude_patients=exclude)
    upper = {c.upper(): c for c in means.columns}
    panel = [g for g in dict.fromkeys(marker_panel(means, detection) + pack_markers) if g in upper]
    signatures = means[[upper[g] for g in panel]]
    signatures.columns = panel
    return signatures, panel, cells


def load_sample(patient: str, keep: set[str]) -> dict:
    dataset = load_visium(VISIUM_DIR / patient, sample_id=patient, keep_genes=keep, max_genes=1500)
    qc = run_qc(dataset.expression, precomputed=dataset.qc_stats)
    passed = np.asarray(qc["passed"], dtype=bool)
    idx = np.where(passed)[0] if passed.sum() >= 50 else np.arange(len(passed))
    library = np.asarray(dataset.qc_stats["total_counts"], dtype=float)[idx]
    expression = dataset.expression.iloc[idx]
    barcodes = [dataset.barcodes[i] for i in idx]
    return {
        "patient": patient,
        "dataset": dataset,
        "log": normalize_counts(expression, log=True, totals=library),
        "linear": normalize_counts(expression, log=False, totals=library),
        "coords": dataset.coordinates[idx],
        "labels": label_array(barcodes, load_labels(patient)),
        "graph": spatial_graph(dataset.coordinates[idx], k=K),
        "model_idx": idx,
    }


def featurize(sample: dict, signatures: pd.DataFrame, panel: list[str]) -> np.ndarray:
    composition, _, _ = nnls_deconvolve(sample["linear"], signatures)
    return build_features(sample["log"], panel, composition, list(signatures.index))


# ── Model ────────────────────────────────────────────────────────────────────


class Sage(torch.nn.Module):
    def __init__(self, n_in: int, n_classes: int, *, graph: bool) -> None:
        super().__init__()
        self.graph = graph
        self.l1_self = torch.nn.Linear(n_in, HIDDEN)
        self.l1_nb = torch.nn.Linear(n_in, HIDDEN, bias=False)
        self.l2_self = torch.nn.Linear(HIDDEN, n_classes)
        self.l2_nb = torch.nn.Linear(HIDDEN, n_classes, bias=False)
        self.drop = torch.nn.Dropout(DROPOUT)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        h = self.l1_self(x)
        if self.graph:
            h = h + self.l1_nb(torch.sparse.mm(adj, x))
        h = self.drop(torch.relu(h))
        out = self.l2_self(h)
        if self.graph:
            out = out + self.l2_nb(torch.sparse.mm(adj, h))
        return out

    def export(self) -> dict[str, np.ndarray]:
        get = lambda t: t.detach().cpu().numpy().astype(np.float32)  # noqa: E731
        zeros1 = np.zeros_like(get(self.l1_nb.weight).T)
        zeros2 = np.zeros_like(get(self.l2_nb.weight).T)
        return {
            "W1_self": get(self.l1_self.weight).T,
            "W1_nb": get(self.l1_nb.weight).T if self.graph else zeros1,
            "b1": get(self.l1_self.bias),
            "W2_self": get(self.l2_self.weight).T,
            "W2_nb": get(self.l2_nb.weight).T if self.graph else zeros2,
            "b2": get(self.l2_self.bias),
        }


def to_torch(features: np.ndarray, graph) -> tuple[torch.Tensor, torch.Tensor]:  # noqa: ANN001
    coo = graph.tocoo()
    adj = torch.sparse_coo_tensor(
        np.vstack([coo.row, coo.col]), coo.data.astype(np.float32), coo.shape
    ).coalesce()
    return torch.from_numpy(features), adj


def class_weights(labels: list[np.ndarray]) -> torch.Tensor:
    counts = np.bincount(np.concatenate([y[y >= 0] for y in labels]), minlength=len(CLASSES))
    weights = 1.0 / np.sqrt(np.maximum(counts, 1))
    weights[counts == 0] = 0.0
    return torch.tensor(weights / weights[counts > 0].mean(), dtype=torch.float32)


def train(
    train_set: list[tuple[np.ndarray, object, np.ndarray]],
    *,
    graph: bool,
    checkpoints: list[int],
    on_checkpoint=None,  # noqa: ANN001
) -> Sage:
    torch.manual_seed(SEED)
    model = Sage(train_set[0][0].shape[1], len(CLASSES), graph=graph)
    optimiser = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights([y for _, _, y in train_set]), ignore_index=-1)
    tensors = [(*to_torch(x, g), torch.from_numpy(y)) for x, g, y in train_set]
    for epoch in range(1, max(checkpoints) + 1):
        model.train()
        optimiser.zero_grad()
        loss = sum(loss_fn(model(x, adj), y) for x, adj, y in tensors) / len(tensors)
        loss.backward()
        optimiser.step()
        if epoch in checkpoints and on_checkpoint is not None:
            model.eval()
            on_checkpoint(epoch, model)
    return model


def predict_logits(model: Sage, features: np.ndarray, graph) -> np.ndarray:  # noqa: ANN001
    model.eval()
    with torch.no_grad():
        x, adj = to_torch(features, graph)
        return model(x, adj).numpy().astype(np.float64)


# ── Metrics ──────────────────────────────────────────────────────────────────


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = logits / temperature
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def scores(y_true: np.ndarray, y_pred: np.ndarray, probs: np.ndarray | None = None) -> dict:
    mask = y_true >= 0
    t, p = y_true[mask], y_pred[mask]
    present = sorted(set(t.tolist()))
    per_class = f1_score(t, p, labels=present, average=None, zero_division=0)
    result = {
        "n_spots": int(mask.sum()),
        "accuracy": round(float((t == p).mean()), 4),
        "macro_f1": round(float(np.mean(per_class)), 4),
        "ari": round(float(adjusted_rand_score(t, p)), 4),
        "per_class_f1": {CLASSES[c]: round(float(f), 4) for c, f in zip(present, per_class, strict=True)},
        "support": {CLASSES[c]: int((t == c).sum()) for c in present},
    }
    if probs is not None:
        result["ece"] = round(expected_calibration_error(probs, y_true), 4)
    return result


def fit_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    mask = labels >= 0
    best, best_nll = 1.0, np.inf
    for t in np.linspace(0.5, 5.0, 46):
        p = softmax(logits[mask], t)[np.arange(mask.sum()), labels[mask]]
        nll = -np.mean(np.log(np.clip(p, 1e-12, None)))
        if nll < best_nll:
            best, best_nll = float(t), nll
    return round(best, 3)


# ── Protocol ─────────────────────────────────────────────────────────────────


def main() -> None:
    started = time.perf_counter()
    pack = get_pack("breast")
    pack_markers = sorted(
        {g.upper() for group in ("cell_types", "zones") for item in pack[group] for g in item["markers"]}
    )

    references = {
        "final": fold_reference(TEST_PATIENTS, pack_markers),
        **{v: fold_reference(TEST_PATIENTS + [v], pack_markers) for v in TRAIN_PATIENTS},
    }
    keep = set(pack_genes(pack))
    for _, panel, _ in references.values():
        keep.update(panel)
    samples = {p: load_sample(p, keep) for p in VISIUM_PATIENTS}
    print(f"loaded {len(samples)} samples in {time.perf_counter() - started:.0f}s; panel sizes",
          {k: len(v[1]) for k, v in references.items()})

    # 1) Inner LOPO CV over TRAIN patients.
    cv: dict[str, dict[int, dict]] = {"gnn": {}, "mlp": {}}
    oof: dict[str, dict[int, list]] = {"gnn": {}, "mlp": {}}
    for val in TRAIN_PATIENTS:
        signatures, panel, _ = references[val]
        feats = {p: featurize(samples[p], signatures, panel) for p in TRAIN_PATIENTS}
        fit_on = [(feats[p], samples[p]["graph"], samples[p]["labels"]) for p in TRAIN_PATIENTS if p != val]
        for kind in ("gnn", "mlp"):
            def record(epoch, model, kind=kind, val=val, feats=feats):  # noqa: ANN001
                logits = predict_logits(model, feats[val], samples[val]["graph"])
                y = samples[val]["labels"]
                cv[kind].setdefault(epoch, {})[val] = scores(y, logits.argmax(axis=1))
                oof[kind].setdefault(epoch, []).append((logits, y))
            train(fit_on, graph=kind == "gnn", checkpoints=EPOCH_GRID, on_checkpoint=record)
        print(f"fold val={val} done ({time.perf_counter() - started:.0f}s)")

    chosen, temperature, cv_summary = {}, {}, {}
    for kind in ("gnn", "mlp"):
        means = {e: float(np.mean([r["macro_f1"] for r in cv[kind][e].values()])) for e in EPOCH_GRID}
        chosen[kind] = max(means, key=means.get)
        logits = np.vstack([lg for lg, _ in oof[kind][chosen[kind]]])
        labels = np.concatenate([y for _, y in oof[kind][chosen[kind]]])
        temperature[kind] = fit_temperature(logits, labels)
        cv_summary[kind] = {
            "mean_macro_f1_by_epoch": {e: round(v, 4) for e, v in means.items()},
            "chosen_epochs": chosen[kind],
            "per_patient": cv[kind][chosen[kind]],
            "temperature": temperature[kind],
            "oof_ece_before": round(expected_calibration_error(softmax(logits), labels), 4),
            "oof_ece_after": round(expected_calibration_error(softmax(logits, temperature[kind]), labels), 4),
        }
        print(kind, "chosen epochs", chosen[kind], "T", temperature[kind], "cv macro-F1", round(means[chosen[kind]], 4))

    # 2) Final model on all TRAIN patients, evaluated once on TEST patients.
    signatures, panel, cells = references["final"]
    feats = {p: featurize(samples[p], signatures, panel) for p in VISIUM_PATIENTS}
    fit_on = [(feats[p], samples[p]["graph"], samples[p]["labels"]) for p in TRAIN_PATIENTS]
    models = {kind: train(fit_on, graph=kind == "gnn", checkpoints=[chosen[kind]]) for kind in ("gnn", "mlp")}

    test: dict[str, dict] = {k: {} for k in ("gnn", "mlp", "topiome_baseline", "always_tumor")}
    pooled: dict[str, list] = {k: [] for k in test}
    for patient in TEST_PATIENTS:
        y = samples[patient]["labels"]
        for kind in ("gnn", "mlp"):
            logits = predict_logits(models[kind], feats[patient], samples[patient]["graph"])
            probs = softmax(logits, temperature[kind])
            pred = probs.argmax(axis=1)
            test[kind][patient] = scores(y, pred, probs)
            pooled[kind].append((y, pred, probs))
        # Topiome's unsupervised baseline on the same spots; "invasive margin" counts as tumour.
        result = run_pipeline(samples[patient]["dataset"], pack, signatures=signatures)
        mapping = {c: i for i, c in enumerate(CLASSES)} | {"invasive_margin": 0}
        zones = np.asarray(result.domains)[samples[patient]["model_idx"]]
        base_pred = np.array([mapping.get(str(z), -1) for z in zones])
        test["topiome_baseline"][patient] = scores(y, base_pred)
        pooled["topiome_baseline"].append((y, base_pred, None))
        majority = np.zeros_like(y)
        test["always_tumor"][patient] = scores(y, majority)
        pooled["always_tumor"].append((y, majority, None))
    for kind, rows in pooled.items():
        y = np.concatenate([r[0] for r in rows])
        p = np.concatenate([r[1] for r in rows])
        probs = np.vstack([r[2] for r in rows]) if rows[0][2] is not None else None
        test[kind]["pooled"] = scores(y, p, probs)

    # NumPy inference must reproduce PyTorch exactly.
    weights = models["gnn"].export()
    patient = TEST_PATIENTS[0]
    reference_logits = predict_logits(models["gnn"], feats[patient], samples[patient]["graph"])
    numpy_logits = forward({k: v.astype(np.float64) for k, v in weights.items()}, feats[patient], samples[patient]["graph"])
    parity = float(np.abs(reference_logits - numpy_logits).max())
    assert parity < 1e-3, f"NumPy/PyTorch mismatch {parity}"

    write_outputs(weights, panel, list(signatures.index), temperature["gnn"], chosen, cv_summary, test, cells, parity, samples)
    print(json.dumps({k: v["pooled"] for k, v in test.items()}, indent=2))
    print(f"done in {time.perf_counter() - started:.0f}s")


def write_outputs(weights, panel, cell_types, temperature, chosen, cv_summary, test, cells, parity, samples) -> None:  # noqa: ANN001, PLR0913
    models_dir = PACKS / "models"
    models_dir.mkdir(exist_ok=True)
    weights_path = models_dir / f"{MODEL_NAME}.npz"
    np.savez_compressed(weights_path, **weights)
    support = {
        group: {
            CLASSES[c]: int(sum((samples[p]["labels"] == c).sum() for p in patients))
            for c in range(len(CLASSES))
        }
        for group, patients in (("train", TRAIN_PATIENTS), ("test", TEST_PATIENTS))
    }
    card = {
        "name": MODEL_NAME,
        "version": VERSION,
        "created": datetime.now(UTC).strftime("%Y-%m-%d"),
        "intended_use": "Research Use Only. Predicts coarse tissue domains on 10x Visium breast cancer sections. "
        "Not for diagnosis, grading, staging or treatment decisions.",
        "model": {
            "architecture": "2-layer GraphSAGE (mean aggregation) over a 6-NN spatial graph, NumPy inference",
            "genes": panel,
            "cell_types": cell_types,
            "classes": CLASSES,
            "k": K,
            "hidden": HIDDEN,
            "temperature": temperature,
        },
        "data": {
            "summary": "Wu et al. 2021 breast cancer Visium (6 patients, pathologist spot annotations; "
            "Zenodo 10.5281/zenodo.4739739, CC BY 4.0) + scRNA reference GSE176078.",
            "train_patients": TRAIN_PATIENTS,
            "test_patients": TEST_PATIENTS,
            "split": "Patient-level. Test patients were never used for reference building, gene selection, "
            "epoch selection or calibration.",
            "label_mapping": "scripts/validation/wu2021_common.py LABEL_TO_ZONE (DCIS, artefact and unlabelled spots ignored)",
            "class_support": support,
            "reference_cells_per_type": cells,
        },
        "training": {
            "framework": "PyTorch (offline); weights exported to NumPy",
            "epochs": chosen["gnn"],
            "learning_rate": LR,
            "weight_decay": WEIGHT_DECAY,
            "dropout": DROPOUT,
            "seed": SEED,
            "loss": "class-weighted cross-entropy (1/sqrt frequency)",
            "selection": "inner leave-one-patient-out CV over train patients, macro-F1",
            "numpy_parity_max_abs_diff": parity,
        },
        "metrics": {"inner_cv": cv_summary, "test": test},
        "limitations": [
            "Six patients from one study and one site; performance on other cohorts, protocols or "
            "Visium HD is unknown.",
            "Labels are coarse, mixed pathology classes; 'invasive margin' and DCIS are not predicted.",
            "Necrosis appears in one training patient only.",
            "Test patients are tumour-dominated; per-class F1 for rare classes rests on few spots.",
        ],
    }
    card_path = models_dir / f"{MODEL_NAME}.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    write_report(card)
    print(f"wrote {weights_path.name}, {card_path.name}")


def _row(name: str, metrics: dict) -> str:
    ece = metrics.get("ece")
    return (
        f"| {name} | {metrics['accuracy']:.3f} | {metrics['macro_f1']:.3f} | {metrics['ari']:.3f} | "
        f"{'—' if ece is None else f'{ece:.3f}'} |"
    )


def write_report(card: dict) -> None:
    test, cv = card["metrics"]["test"], card["metrics"]["inner_cv"]
    names = {
        "gnn": "GNN (spatial graph)",
        "mlp": "MLP (same features, no graph)",
        "topiome_baseline": "Topiome baseline (k-means + markers)",
        "always_tumor": "Always 'tumor'",
    }
    lines = [
        "# Breast cancer domain model — Wu et al. 2021 validation",
        "",
        f"_Model `{card['name']}` v{card['version']} · {card['created']} · Research Use Only_",
        "",
        "## Split (patient-level)",
        "",
        f"- **Train (4):** {', '.join(card['data']['train_patients'])}",
        f"- **Test (2, held out):** {', '.join(card['data']['test_patients'])}",
        f"- {card['data']['split']}",
        "",
        "## Held-out test (pooled over test patients)",
        "",
        "| Model | Accuracy | Macro-F1 | ARI | ECE |",
        "|---|---:|---:|---:|---:|",
        *[_row(names[k], test[k]["pooled"]) for k in names],
        "",
        "## Per test patient",
        "",
        "| Model | Patient | Accuracy | Macro-F1 | ARI |",
        "|---|---|---:|---:|---:|",
    ]
    for k in names:
        for patient in card["data"]["test_patients"]:
            m = test[k][patient]
            lines.append(f"| {names[k]} | {patient} | {m['accuracy']:.3f} | {m['macro_f1']:.3f} | {m['ari']:.3f} |")
    lines += [
        "",
        "Per-class F1 (GNN, pooled): "
        + ", ".join(f"{c} {v:.2f}" for c, v in test["gnn"]["pooled"]["per_class_f1"].items()),
        "",
        "Test support: " + ", ".join(f"{c} {n}" for c, n in test["gnn"]["pooled"]["support"].items()),
        "",
        "## Inner cross-validation (train patients only)",
        "",
        f"- GNN: chosen {cv['gnn']['chosen_epochs']} epochs, temperature {cv['gnn']['temperature']} "
        f"(OOF ECE {cv['gnn']['oof_ece_before']} → {cv['gnn']['oof_ece_after']})",
        f"- MLP: chosen {cv['mlp']['chosen_epochs']} epochs, temperature {cv['mlp']['temperature']}",
        "",
        "| Epochs | GNN macro-F1 | MLP macro-F1 |",
        "|---:|---:|---:|",
        *[
            f"| {e} | {cv['gnn']['mean_macro_f1_by_epoch'][e]:.3f} | {cv['mlp']['mean_macro_f1_by_epoch'][e]:.3f} |"
            for e in cv["gnn"]["mean_macro_f1_by_epoch"]
        ],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in card["limitations"]],
        "",
        "Reproduce: `cd apps/api && uv run python -I ../../scripts/validation/build_reference_wu2021.py && "
        "uv run --with torch python -I ../../scripts/validation/train_domain_gnn.py`",
        "",
    ]
    out = ROOT / "docs" / "validation" / "breast-wu2021.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
