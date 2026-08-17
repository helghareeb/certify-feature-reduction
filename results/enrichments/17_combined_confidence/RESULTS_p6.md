# RESULTS — P6: combined-confidence audit (12 clinical datasets, COMPLETE)

**Run:** second compute node · **2026-08-16 ~06:45 AST** · approved enrichment P6, pre-registered in
`PRESPEC_p6.md` (combination rule locked 2026-08-14, before any P6 number). Now COMPLETE over all **12
clinical datasets** (the diabetes130 −d tail finished 06:29 on the full 101,763-row cohort). Frozen code
untouched; reuses the cached OOF predictions + recomputes −d via BallTree (no refit). 2160 cells
(12 datasets × 3 rankers × {logistic,rf} × 30 reps), paired folds, bootstrap 95% CI over cells.

## Question (audit framing, not a method claim)
Reduction imposes a selective-reliability harm (AURC penalty). Does a confidence signal **independent of the
predicted probability** (−d, distance-to-training-support) **mitigate** it? Headline quantity = whether the
penalty *shrinks*, reported for all three arms side by side — never C alone.

## Arms (identical evaluation on the SAME cached OOF predictions)
- **A** = |p−0.5| (the paper's existing probability-margin confidence, baseline)
- **B** = −d (X-only mean Euclidean distance to the 10 nearest training neighbours, train-fold standardised)
- **C** = LOCKED combined = `0.5·(rank01(|p−0.5|) + rank01(−d))` within each held-out fold (MEAN of the two
  rank-normalised signals — chosen in advance, NOT tuned; MIN was not tried-and-cherry-picked)

## Result 1 — AURC selective-ranking penalty (aggressive frac:0.25 − full frac:1; lower AURC = better)
| arm | signal | AURC full | AURC aggr | penalty [95% CI over 2160 cells] |
|--|--|--:|--:|--:|
| A | \|p−0.5\| | 0.0826 | 0.1160 | **+0.0335 [+0.0318, +0.0351]** |
| B | −d | 0.1526 | 0.1642 | +0.0116 [+0.0103, +0.0129] |
| C | combined | 0.1048 | 0.1221 | **+0.0173 [+0.0163, +0.0183]** |

**Combined confidence mitigates 48.3% of the reduction penalty vs the probability-margin baseline**
(+0.0335 → +0.0173), CIs disjoint. This is **pre-specified outcome 1** (C materially smaller than A → an
independent confidence mitigates part of the measured harm). The mitigation is **positive on all 12
datasets** (per-dataset table in `p6_perdataset_mitigation.csv`); largest on haberman (74%), bcw (69%),
diabetes130 (59%); negligible-penalty datasets (wdbc, spectf, hepatitis) show tiny/near-zero effects as
expected (spectf's baseline penalty is ~0.0004, so its "%" is an unstable artifact — combined is very
slightly beneficial there).

## Result 2 — selective net benefit @ coverage 0.8 (HONEST counter-axis: combined does NOT help here)
| arm | selNB penalty (aggr − full) [95% CI] |
|--|--:|
| A (\|p−0.5\|) | −0.00970 [−0.01096, −0.00850] |
| C (combined) | **−0.01631 [−0.01761, −0.01503]** |

On the decision-analytic axis the picture **reverses**: the combined ordering's selective net-benefit
penalty is *larger* (more negative) than the probability-margin baseline. So −d improves the **ranking**
(AURC) robustness under reduction but does **not** improve **thresholded clinical net benefit** at 80%
coverage — because net benefit is driven by the calibrated probability at the decision threshold, which −d
does not carry. **We report both axes side by side, as pre-registered; we do not present the favourable AURC
axis alone.**

## Honest conclusion (audit, not a proposed method)
An independent, X-only confidence signal **partly rescues the selective-ranking degradation** that reduction
causes (≈48% of the AURC penalty, robust across all 12 datasets and both learners), **but the rescue is
specific to the ranking axis** — it does not carry over to thresholded net benefit. Practically: if a
deployed selective classifier abstains by *ordering* confidence, adding distance-to-support meaningfully
softens reduction's harm; if it abstains by a *net-benefit threshold*, the probability margin alone remains
the operative signal. Full method treatment (baselines, operating points, cost model) is a separate future
paper, as pre-registered.

## Provenance / integrity
Reuses cached OOF p (results/cache/poof), recomputes −d with the SAME per-fold firewall as Tier 6 (BallTree
on train-fold only, standardised on train μ/σ, train-median impute). diabetes130 loaded at the **full
101,763-row cohort** (params from config; the earlier 6000-subsample bug does NOT affect this run). Combined
rule byte-locked in PRESPEC_p6.md before computation. R6: separate artifact.

## Deliverables (flat zip, code inside per N17)
`RESULTS_p6.md` · `p6_summary_12clinical.csv` (arm-level, both axes, CIs) ·
`p6_arms_12clinical.csv` (all 2160 cells) · `p6_arms.csv` (11-set component) ·
`p6_arms_diabetes130.csv` (d130 component) · `p6_perdataset_mitigation.csv` · `compute_p6.py` (exact code) ·
`PRESPEC_p6.md` · `DONE.md` · `MANIFEST.sha256`.
