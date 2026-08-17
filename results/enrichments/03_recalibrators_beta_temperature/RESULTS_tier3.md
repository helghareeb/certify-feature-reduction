# RESULTS — Tier 3: a third + fourth recalibrator (beta calibration + temperature scaling)

**Run:** second compute node · **2026-08-15 ~06:10 AST** · per `the Tier 3-5 addendum` T3.1. **12/12 datasets**
(11 small + diabetes130 full 101,763 cohort), reduced grid (full frac:1 vs aggressive frac:0.25), 3
rankers × 3 learners, 30 reps.

## Accuracy provenance
Frozen `run.py` untouched. beta/temperature computed by a separate module that replicates
`CalibratedClassifierCV(cv=3, ensemble=True)` on the same folds/seeds, **verified to reproduce the
cached sigmoid p_oof to 2.2×10⁻¹⁶** before any beta/temp number was trusted (`none/sigmoid/isotonic`
delegate to the original frozen code). Existing calibrated results were never recomputed.

## T3.1 — the dissociation holds for the third and fourth recalibrator
Mean metric at full budget over 12 datasets × 3 rankers × 3 learners; Δ vs calibrate=none:

| metric | none | temperature (1-param) | beta (3-param) |
|---|--:|--:|--:|
| **ECE** (calibration error) | 0.0694 | 0.0640 (**−8%**) | 0.0504 (**−28%**) |
| **AURC** (selective reliability) | 0.0840 | 0.0814 (−3%) | 0.0845 (**+0.6%**) |
| **net benefit** (clinical utility) | 0.2960 | 0.2961 (0%) | 0.2985 (**+0.8%**) |

**ECE recovers, AURC and net benefit do not** — for temperature (1 parameter) and for beta (3
parameters), just as §4.8 reported for isotonic. Beta is the decisive case: it is a **flexible**
parametric recalibrator that cuts ECE by 28% yet moves AURC and net benefit by essentially zero.

## Reading (pre-ruled: dissociation confirmed for the new recalibrators)
§4.8 argues the failure to recover AURC/net-benefit is **not a flexibility limitation**, evidenced by
isotonic. Adding beta and temperature makes that much harder to dispute: across four recalibrators
spanning 1→3 parameters→nonparametric, **ECE recovery scales with flexibility while AURC/net-benefit
recovery stays flat at ~0.** (The formal flexibility-ladder figure is enrichment P2.) A recalibrator
that halves calibration error while leaving selective reliability and clinical utility untouched is the
core evidence that these are dissociated properties, not a single "poorly-calibrated" axis.

## Deliverables
`RESULTS_tier3.md` · `summary_tier3_11ds.csv` · `summary_tier3_d130.csv` (full per-cell, both) ·
`PRESPEC_p6.md`-independent (P6 is a separate experiment) · `DONE.md` · `MANIFEST.sha256`. Separate
artifact/hash (R6). Numbers, not caches.
