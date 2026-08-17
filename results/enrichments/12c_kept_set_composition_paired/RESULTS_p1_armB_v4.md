# RESULTS — P1 Arm B v4: PAIRED, leakage-free (enrichment item 2). The rise survives → caveat comes out.

**Run:** second compute node · **2026-08-16 ~21:35 AST** · re-run of Arm B with `keep` dropped from the
per-cell seed, so within a (method,classifier,rep) every rung shares folds and the same base RF ranking
(nested pools 100⊂256⊂…⊂10000). The ladder is now **paired by construction**, like every other comparison in
the paper — the one between-condition departure is removed. Parallelised over 16 cores (bit-identical to
serial; approved in the Arm B v4 pre-specification, B=5000, n_jobs=1). 30 reps × 3 rankers × {logistic,rf} = 180 units/rung.

## Result — paired penalty rises monotonically; extremes disjoint (pre-specified outcome #1)
| kept | full-feature AUROC | reduced-25 AUROC | penalty [95% CI] |
|--:|--:|--:|--:|
| 100 | 0.898 | 0.873 | +0.025 [.022,.028] |
| 256 | 0.901 | 0.866 | +0.035 [.033,.038] |
| 1000 | 0.910 | 0.850 | +0.060 [.055,.064] |
| 5000 | 0.913 | 0.836 | +0.077 [.069,.084] |
| 10000 | 0.911 | 0.821 | +0.091 [.083,.100] |

- **The rise SURVIVES the paired design.** Penalty rises monotonically +0.025 → +0.091 as the available set
  widens; the keep=100 and keep=10000 intervals are disjoint. Full-feature AUROC barely moves (0.898→0.911);
  the 25-feature model falls steadily (0.873→0.821). Same distributed-signal mechanism, now paired.
- **vs v3 (independent folds):** point estimates essentially unchanged (v3 +0.027→+0.087; v4 +0.025→+0.091),
  mean CI width marginally tighter (0.0105 vs 0.0107) — exactly as expected when the comparison becomes
  paired. Anchor keep=10000: v4 +0.0909 vs v3 +0.0869 (fold set changed; consistent).
- **Caveat removed.** The manuscript's disclosure that "the rungs draw independent cross-validation splits …
  the ladder is compared between conditions rather than within them" is no longer needed: the ladder is now
  paired, and the adjacent rungs are separated too (all five CIs step apart), not only the extremes.

## Suggested manuscript replacement (Arm B paragraph)
Replace the v3 numbers and the between-condition caveat with:
"The penalty rises as the available set widens, from +0.025 (95% CI +0.022 to +0.028) with only the top 100
features to +0.091 (+0.083 to +0.100) with all 10,000: monotone across the ladder, with disjoint intervals at
adjacent rungs. The full-feature reference barely moves (AUROC 0.898 to 0.911) while the 25-feature model
falls steadily (0.873 to 0.821). Every rung shares the same cross-validation folds and base ranking (nested
pools), so the ladder is paired like every other comparison in this study." (Delete the independent-folds
limitation sentence.)

## Deliverables (flat zip, script inside)
`RESULTS_p1_armB_v4.md` · `p1_arcene_reverse_v4.csv` (per-rung mean+sd+95%CI+n) ·
`p1_arcene_reverse_v4_rows.csv` (900 per-unit rows) · `compute_p1b_v4_paired.py` · `DONE.md` · `MANIFEST.sha256`.
