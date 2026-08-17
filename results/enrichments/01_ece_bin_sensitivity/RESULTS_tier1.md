# RESULTS — Tier 1 (calibration/selective-reliability sensitivity)

**Run:** second compute node · **2026-08-13 ~10:40 AST** · code commit `e073ad5`, env byte-identical (Stage 0 gate).
**Coverage:** `none` = all 12 datasets; `sigmoid`/`isotonic` = 11 datasets (**diabetes130 calibrated arm pending** — ~1–2 days, see `QUERY_tier1_diabetes130_calibrated_cost.md`). Aggregation: mean over datasets × 3 reduction methods × 30 reps; reduction penalty = metric(25% budget, frac:0.25) − metric(full, frac:1).

## T1.1 — widened cache + reduced grid
`config/calibration_tier1.json` = committed config with `persist.p_oof_cells` widened to 12 × 3 methods × {logistic,rf} × {none,sigmoid,isotonic} (216 cells); everything else byte-identical. Ran the reduced grid (`--classifiers logistic rf`). **New config hash by design — this is a separate sensitivity artifact and must NOT be merged with the submitted grid (R6).** OOF probabilities cached per cell×rep; tables below are computed from those caches with the repo's exact ECE (equal-width, weighted |acc−conf|) and AURC (trapezoid risk–coverage).

## 🔬 T1.2 — ECE reduction-penalty bin sweep  → `tier1_ece_binsweep.csv`
Bin counts {5,10,15,20,30,50}, equal-width **and** equal-frequency. Direction of the penalty (positive = reduction worsens ECE, the manuscript's claim) per (learner, calibrator), equal-width:

| learner | calibrator | b5 | b10 | b15 | b20 | b30 | b50 | stable? |
|---|---|--:|--:|--:|--:|--:|--:|:--:|
| logistic | **none** | −0.0021 | −0.0009 | +0.0021 | +0.0012 | +0.0021 | +0.0003 | ❌ **FLIPS** |
| logistic | sigmoid | +0.0031 | +0.0072 | +0.0082 | +0.0076 | +0.0068 | +0.0061 | ✅ |
| logistic | isotonic | +0.0126 | +0.0098 | +0.0093 | +0.0076 | +0.0073 | +0.0046 | ✅ |
| rf | none | +0.0224 | +0.0220 | +0.0215 | +0.0200 | +0.0189 | +0.0169 | ✅ |
| rf | sigmoid | +0.0007 | +0.0026 | +0.0022 | +0.0014 | +0.0008 | +0.0001 | ✅ |
| rf | isotonic | +0.0091 | +0.0071 | +0.0068 | +0.0057 | +0.0049 | +0.0037 | ✅ |

**Finding (reported per the pre-ruling — no bin-count cherry-picking):**
- The penalty's **direction is robust to bin count in 5 of 6 learner×calibrator cells**, across both equal-width and equal-frequency binning.
- **The one exception is uncalibrated logistic:** at coarse bins (5, 10) the sign is *negative* (reduction slightly *improves* ECE), at bins ≥15 it is *positive*. **At the manuscript's fixed bins=15 the reported direction holds, but it is not robust to bin count for that single cell.**
- **Calibration removes the instability:** both sigmoid and isotonic logistic are stably positive at every bin count. Equal-frequency binning shows no additional flips.
- **Interpretation:** the manuscript's ECE conclusions survive the bin-sensitivity check everywhere *except* the uncalibrated-logistic cell; the honest statement is "robust under calibration and for rf; bin-count-sensitive only for uncalibrated logistic." This directly addresses the "we did not run a bin-count sensitivity sweep" limitation — it can now be replaced with this result rather than deleted outright.

### T1.2b — MATERIALITY of the flip (Holm-corrected)  → `tier1_ece_materiality.csv`
Per your follow-up: is the logistic flip *material*, or a sign change inside noise? Test — unit = (dataset, method), unit penalty = mean over 30 reps; one-sample t-test (+ Wilcoxon) of unit penalties vs 0, Holm-corrected across the 6 bin counts; material iff `p_holm < stat_alpha (0.05)`.

- 🔴 **The logistic sign flip is a sign change INSIDE NOISE — not material at ANY bin count.** For `logistic/none`, equal-width: signs are −,−,+,+,+,+ but **every p_holm = 1.0** (none material); equal-frequency: **no flip at all** (all +), and none material (p_holm 0.15–0.64). So the uncalibrated-logistic ECE reduction penalty is **statistically indistinguishable from zero regardless of bin count or binning** — the weaker, cleaner statement: no material ECE conclusion exists for that cell, so there is nothing for a bin choice to rescue or overturn.
- **Where the crossover is:** `logistic/none` equal-width changes sign **between 10 and 15 bins**; equal-frequency does **not** cross (stays positive) — the crossover is an artifact of equal-width binning, and it is immaterial either way.
- **Where materiality actually lives:** `rf/none` is **material at all six bin counts under equal-frequency** binning, but **not material at any** under equal-width; `rf/isotonic` and `rf/sigmoid` are material at the mid bin counts under equal-frequency. So for the cells whose penalty *is* real (rf), **materiality depends on the binning scheme (equal-frequency detects it, equal-width misses it)** more than on the bin count.
- **Phrasing this supports:** "The ECE reduction penalty is not material for uncalibrated logistic at any bin count or binning (the apparent 15-bin sign is within noise); for rf it is material but only under equal-frequency binning. The a-priori fixed 15 equal-width bins therefore neither manufactures nor hides a *material* logistic effect, but does miss the material rf effect that equal-frequency binning reveals." No bin count was selected to favor any conclusion.

## 🔬 T1.3 — AURC under alternative confidence measures  → `tier1_aurc_confidence.csv`
AURC reduction penalty recomputed with confidence = |p−0.5| (manuscript), margin |2p−1|, and predictive entropy:
- **|p−0.5| and |2p−1| give identical AURC** (exact — both are monotone rescalings of |p−0.5|).
- **Predictive entropy differs by ≤ 6.7e−03** (a floating-point/clipping effect at the probability extremes; not an ordering change of substance).
- **The AURC reduction penalty survives, essentially invariant to the confidence choice**, for every learner × calibrator. This **quantifies and confirms** the manuscript's own concession that, because confidence is a monotone function of the predicted probability, selective reliability and calibration "move in tandem." (A confidence signal *independent* of p — not requested here — would be needed to break the tie.)

## Deliverables (numbers only — raw caches NOT shipped, per rule)
`tier1_ece_binsweep.csv` · `tier1_aurc_confidence.csv` · this `RESULTS_tier1.md` · `calibration_tier1.json` (the config) · `env_freeze.txt` · `DONE.md` · `MANIFEST.sha256`.
**Pending:** diabetes130 calibrated arm (your call in the QUERY); the tables above hold at 11/12 datasets for the calibrated arms and 12/12 for `none`.
