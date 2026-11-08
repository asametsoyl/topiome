# Topiome

**Computational research on cellular responses to defined perturbations — Research Use Only.**

Topiome is exploring whether computational models can predict cellular responses to defined perturbations in biological contexts that were not used during training. The active project uses four public perturbation-response benchmark sources: three CRISPR Perturb-seq screens and one drug screen. Zero-shot context transfer passed an in-dataset gate in Replogle-Nadig but failed independent replication on X-Atlas/Orion (0/2 numeric folds); that line is stopped. A different, pre-registered task — calibrating transfer with a 100-condition pilot in the target cell line — passed on Tahoe-100M (5/5 rules, median ~2% RMSE gain over the pilot mean), but the effect is modest and gene ranking did not improve. The exploratory unseen-perturbation check was also negative. **Topiome has not trained or validated a general perturbation-response model, its only positive independent result requires pilot measurements, and no result has been tested prospectively in a lab.**

The previous spatial-transcriptomics product is retained as legacy code and documented separately. Its results do not support claims about the new research direction.

## Research premise

- Start with public perturbation-response measurements whose reuse terms are documented.
- Test unseen perturbations and contexts with leakage-resistant splits.
- Compare against simple baselines before using more complex models.
- Report biological-response metrics and calibrated uncertainty.
- Require independent experimental measurements before making prospective biological claims.

## Development

```bash
# Requirements: Node >= 22, uv, Python 3.12; Docker is optional
bash scripts/setup.sh
npm run dev
```

- Web: http://localhost:3000
- API: http://localhost:8000/docs
- New account registration is paused. Existing accounts open the legacy spatial workspace.

## Data policy

Public research datasets stay under local `data/perturbation/` and are excluded from git. Before use, record the exact source, dataset-level license, retrieval date, hash, assay/context labels, and allowed use. Do not place human-subject data, credentials, or personally identifying information in the repository, demo seed, or logs.

## Project docs

| File | Purpose |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Project rules for contributors and agents |
| [`docs/STATUS.md`](docs/STATUS.md) | Current work, next steps, and decisions |
| [`docs/PRODUCT.md`](docs/PRODUCT.md) | New research product direction |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | Perturbation benchmark and scientific gates |
| [`docs/DATA.md`](docs/DATA.md) | Dataset selection, rights, and local storage |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Architecture and product decisions |
| [`docs/legacy/`](docs/legacy/) | Archived spatial-product evidence and status |

## RUO boundary

> **For Research Use Only.** Topiome is not intended for diagnosis, prognosis, treatment selection, patient management, or clinical decision-making. Research predictions are hypotheses and require independent validation.

## License

Proprietary. All rights reserved. Dataset licenses are separate and recorded per source.
