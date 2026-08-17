# RESULTS — the enrichment round E3: cross-axis coherence of the reduction penalty (CORRECTED orientation)

**Run:** second compute node · **2026-08-16 01:05 AST** · CORRECTED after the agent caught a sign error:
`conformal_efficiency` = mean prediction-SET SIZE (lower is better, verified in metrics.py:129), so its
harm-oriented penalty is +delta (worse = larger sets) and must NOT be negated. v1 negated it, flipping its
4 correlations. Magnitudes were all correct; only that column's sign was wrong. Orientation is now
ASSERTED in code (all off-diagonals must be positive under harm-orientation) -- the check passes.

## Corrected cross-axis Spearman matrix (harm-oriented penalty, 108 cells, all positive)
|  | ECE | AURC | net_benefit | conformal_setsize | selective_ECE |
|---|--:|--:|--:|--:|--:|
| **ECE** | 1.00 | 0.30 | 0.60 | 0.30 | 0.97 |
| **AURC** | 0.30 | 1.00 | 0.66 | **0.885** | 0.31 |
| **net_benefit** | 0.60 | 0.66 | 1.00 | 0.775 | 0.62 |
| **conformal_setsize** | 0.30 | 0.885 | 0.775 | 1.00 | 0.315 |
| **selective_ECE** | 0.97 | 0.31 | 0.315 | 0.315 | 1.00 |

## Reading -- two coherent groups, nearly independent (a sharper result than v1's "axes disagree")
- **ORDERING axes move together:** AURC ↔ conformal set size = **+0.885** (both defined on the ordering
  of predicted probabilities).
- **SCALE axes move together:** ECE ↔ selective-ECE = **+0.97** (both defined on the probability scale;
  also the sanity check -- two views of one quantity).
- **The two groups are nearly independent:** ECE ↔ AURC = **+0.30**.

So reduction's damage separates cleanly into a *scale* dimension (calibration) and an *ordering* dimension
(selective reliability / conformal), which are largely decoupled. This arrives at the SAME split the
recalibration ladder (P2) implies mechanically -- recalibration acts on the scale and cannot repair an
ordering -- so two independent routes give the same structure. (Now in the manuscript Discussion.)

## Habit added (from the finding)
**Assert the orientation, don't just document it.** The v1 header said "positive = worse" for all axes
but the data disagreed for one; only recomputation could tell. The corrected code asserts every
off-diagonal is positive under harm-orientation (a stated convention nothing checks is a comment, not a
constraint) -- beside "numbers into JSON", "cell counts", "dispersion".

## Deliverables
`RESULTS_e3.md` · `e3_cross_axis_corr.csv` · `e3_summary.json` · `DONE.md` · `MANIFEST.sha256`. Supersedes
the mixed-sign v1.
