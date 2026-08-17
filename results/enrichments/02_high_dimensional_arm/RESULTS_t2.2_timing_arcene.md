# T2.2 — timing probe (Arcene, the top-recommended high-dim pick)

**Run:** second compute node · **2026-08-13 ~13:45 AST** · one stratified fold, raw X,Y fed to the repo's own
`reduction.rank` + `run._fit_predict` (mirrors `probe_timing.py`; **no loader written, no config extended**).
Ran on Arcene (n=200, p=10,000, prevalence 0.44) as the near-certain pick; rerun trivially on whichever set you confirm.

## Measured atomic costs (one fold)
| op | seconds |
|---|--:|
| rank mutual_info | 13.53 |
| rank rf_importance | 2.72 |
| rank l1_logistic | 3.28 |
| fit logistic k=10000 / k=4 | 1.89 / 0.01 |
| fit rf k=10000 / k=4 | 2.10 / 0.13 |
| fit gb k=10000 / k=4 | 11.00 / 0.06 |
| fit rf+isotonic / rf+sigmoid (k=full) | 3.40 / 3.37 |
| **peak RSS** | **310 MB** |

## Feasibility read
- **RAM is a non-issue** (310 MB peak) — these small-n/large-p sets allow high shard concurrency, unlike diabetes130.
- **Cost is hours, not days.** The expensive atoms are `mutual_info` ranking (13.5s) and `gb` full-k fit (11s); everything at reduced budgets is ~instant. With n=200 the per-fold work is ~40s; the full grid (3 methods × 5 folds × 30 reps × budgets × calibrators) projects to a **few GPU-free CPU hours per dataset**, not the multi-day regime diabetes130 hit.
- Larger-p picks (SMK-CAN p≈20k, GLI-85 p≈22k) roughly double the ranking cost but keep small n → still hours.
- Machine-readable: `timing_probe_arcene.json`.

**Conclusion:** the p≫44 arm is tractable on this box. Awaiting your dataset sign-off (T2.1) before any loader/config or full run.
