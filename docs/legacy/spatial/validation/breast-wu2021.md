# Breast cancer domain model — Wu et al. 2021 validation

_Model `breast_domain_gnn_v1` v1.0.0 · 2026-11-06 · Research Use Only_

## Split (patient-level)

- **Train (4):** 1142243F, 1160920F, CID4290, CID44971
- **Test (2, held out):** CID4465, CID4535
- Patient-level. Test patients were never used for reference building, gene selection, epoch selection or calibration.

## Held-out test (pooled over test patients)

| Model | Accuracy | Macro-F1 | ARI | ECE |
|---|---:|---:|---:|---:|
| GNN (spatial graph) | 0.770 | 0.446 | 0.260 | 0.098 |
| MLP (same features, no graph) | 0.739 | 0.386 | 0.191 | 0.136 |
| Topiome baseline (k-means + markers) | 0.325 | 0.210 | 0.011 | — |
| Always 'tumor' | 0.856 | 0.231 | 0.000 | — |

## Per test patient

| Model | Patient | Accuracy | Macro-F1 | ARI |
|---|---|---:|---:|---:|
| GNN (spatial graph) | CID4465 | 0.769 | 0.559 | 0.195 |
| GNN (spatial graph) | CID4535 | 0.770 | 0.613 | 0.326 |
| MLP (same features, no graph) | CID4465 | 0.754 | 0.435 | 0.181 |
| MLP (same features, no graph) | CID4535 | 0.722 | 0.537 | 0.214 |
| Topiome baseline (k-means + markers) | CID4465 | 0.306 | 0.223 | -0.004 |
| Topiome baseline (k-means + markers) | CID4535 | 0.348 | 0.330 | 0.114 |
| Always 'tumor' | CID4465 | 0.937 | 0.323 | 0.000 |
| Always 'tumor' | CID4535 | 0.761 | 0.288 | 0.000 |

Per-class F1 (GNN, pooled): tumor_core 0.86, stroma 0.48, immune_aggregate 0.29, normal_gland 0.15

Test support: tumor_core 1913, stroma 250, immune_aggregate 69, normal_gland 3

## Inner cross-validation (train patients only)

- GNN: chosen 25 epochs, temperature 2.3 (OOF ECE 0.1236 → 0.0748)
- MLP: chosen 25 epochs, temperature 1.8

| Epochs | GNN macro-F1 | MLP macro-F1 |
|---:|---:|---:|
| 25 | 0.452 | 0.430 |
| 50 | 0.446 | 0.412 |
| 100 | 0.436 | 0.405 |
| 150 | 0.445 | 0.407 |
| 200 | 0.444 | 0.397 |
| 300 | 0.440 | 0.400 |

## Limitations

- Six patients from one study and one site; performance on other cohorts, protocols or Visium HD is unknown.
- Labels are coarse, mixed pathology classes; 'invasive margin' and DCIS are not predicted.
- Necrosis appears in one training patient only.
- Test patients are tumour-dominated; per-class F1 for rare classes rests on few spots.
- Epoch selection picked the smallest grid value (25); the grid was not extended after seeing test results to avoid test-set tuning. A v2 should extend the grid and use a fresh held-out cohort.
- Held-out ARI 0.26 is below the VALIDATION.md minimum (0.35): the breast pack stays **beta**.
- 'Always tumor' has higher raw accuracy because 86% of test spots are tumour; macro-F1 and ARI are the meaningful measures here.

Reproduce: `cd apps/api && uv run python -I ../../scripts/validation/build_reference_wu2021.py && uv run --with torch python -I ../../scripts/validation/train_domain_gnn.py`
