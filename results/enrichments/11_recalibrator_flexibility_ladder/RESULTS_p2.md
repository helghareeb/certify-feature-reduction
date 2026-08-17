# RESULTS — P2: the recalibrator flexibility ladder (CORRECTED — matched all-ranker grid)

**Run:** second compute node · **2026-08-15 ~16:15 AST** · CORRECTED after the review caught a
grid-mismatch in the first version. Corrected result is *stronger*.

## 🔴 Correction (honest record)
The first P2 ladder mixed two files with different grid coverage: none/sigmoid/isotonic came from
`summary_recalibration.csv` — which is **mutual_info-only (36 cells/rung)** — while temperature/beta came
from the tier3 summaries (**all 3 rankers, 108 cells/rung**). That compared a one-ranker mean against
three-ranker means and merged three `calib_sha256` values into one table (an R6 violation). The
`none`-baseline agreeing to ~1e-4 was a coincidence of similar means, **not** proof of the same
population. I used the only baseline file I had (the mutual_info-only one); the all-ranker recalibration
summary lives on the box (from the 20-h all-rankers control). Corrected below on the matched
all-ranker grid — 108 cells at every rung, `none` baselines identical to 0.00e+00 across all three axes.

## The ladder — matched grid (12 datasets × 3 rankers × 3 learners = 108 cells/rung, full budget)
Recovery signed so positive = improvement: ECE_rec=ECE(none)−ECE(cal); AURC_rec=AURC(none)−AURC(cal);
NB_rec=NB(cal)−NB(none).

| recalibrator | params | ECE | ECE recovery | AURC | AURC recovery | NB recovery | cells |
|---|:--:|--:|--:|--:|--:|--:|--:|
| none | 0 | 0.0694 | +0.0000 | 0.0840 | +0.0000 | +0.0000 | 108 |
| temperature | 1 | 0.0640 | +0.0054 | 0.0814 | +0.0026 | +0.0001 | 108 |
| sigmoid | 2 | 0.0542 | +0.0152 | 0.0844 | −0.0004 | +0.0021 | 108 |
| beta | 3 | 0.0504 | +0.0191 | 0.0845 | −0.0005 | +0.0024 | 108 |
| isotonic | nonparametric | 0.0501 | +0.0193 | 0.0853 | −0.0013 | +0.0028 | 108 |

## Result — stronger than the first version
- **Spearman(flexibility, ECE recovery) = +1.000 (exactly).** Strictly monotone at every rung — on the
  matched grid isotonic recovers strictly more ECE than beta (+0.0193 vs +0.0191); the beta/isotonic tie
  that gave +0.949 before was the mixed-grid artifact.
- **AURC recovery flat and slightly negative** (mean |AURC_rec| = 0.0010; ρ(flexibility, AURC_rec)=−0.900).
- **Net-benefit recovery ~0** across all rungs.

## Reading (unchanged in substance, harder in evidence)
Across a five-rung ladder from 0→1→2→3→nonparametric parameters, **ECE recovery rises perfectly
monotonically while selective reliability (AURC) and clinical utility (net benefit) do not recover at any
rung.** "Not a flexibility limitation" is now a strictly-monotone ECE-recovery curve against a flat AURC
line, on ONE grid, with an exact baseline match — the strongest possible form of the claim.

## Process fixes adopted (from the finding)
1. Every headline number is now written into `p2_summary.json` (incl. the Spearman value), not only prose.
2. Per-rung cell counts are stated (all 108 here) so a grid mismatch is visible at a glance.
Independent check CONFIRMED on the second compute node: all-ranker none/sigmoid/isotonic ECE recomputed from the
p_oof cache (9,720 cells, metrics.expected_calibration_error) = none 0.0694 / sigmoid 0.0542 / isotonic
0.0501 -> recovery +0.0152 / +0.0193, IDENTICAL to the matched-grid figures. The correction reproduces locally.

## Deliverables
`RESULTS_p2.md` (this, corrected) · `p2_flexibility_ladder.csv` (matched grid) · `p2_summary.json`
(with Spearman + cell counts) · `DONE.md` · `MANIFEST.sha256`. Supersedes the mixed-grid version.
