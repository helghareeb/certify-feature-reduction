# RESULTS — P5 matched-budget width test across k∈{1,2,4,8} (enrichment item 1)

**Run:** second compute node · **2026-08-16** · cache-only re-analysis, no fitting. Clinical panel only
(never pooled with the high-dimensional arm). harm = AUROC(full) − AUROC(reduced-to-k); Spearman ρ(p, harm)
with p-value and a 5000-resample bootstrap CI (resampling datasets). A dataset qualifies at budget k only if
p>k (genuine reduction). Source: `results/summary.csv`. Script: `compute_p5_across_budgets.py`.

## Result — the width association holds on the FULL panel from k=2 up; the 9/12 caveat is removed
| budget k | datasets | Spearman ρ(p, harm) | p-value | bootstrap 95% CI | material? |
|--:|--:|--:|--:|--:|:--|
| 1 | **12** | +0.323 | 0.306 | [−0.304, +0.712] | no (CI spans 0) |
| **2** | **12** | **+0.600** | **0.039** | **[+0.015, +0.915]** | **yes** |
| 4 | 11 | +0.685 | 0.020 | [+0.108, +0.971] | yes |
| 8 | 9 | +0.765 | 0.016 | [+0.175, +0.996] | yes |

## Reading (against pre-specified outcome 1)
- The matched-budget width effect is **demonstrated on the full 12-dataset panel**: at k=2 it is material
  (ρ=+0.60, p=0.039, CI excludes 0) **including the three narrowest datasets** (haberman p=3, mammographic
  p=5, pima p=8) that k=8 had to drop. **The nine-of-twelve restriction is no longer needed** — the claim
  can be stated on the whole panel.
- It **strengthens monotonically** as the budget loosens (k=2→4→8: +0.60→+0.69→+0.77).
- At **k=1 it is not significant** (ρ=+0.32, CI spans zero). This is coherent, not a failure: reducing every
  dataset to a single feature harms them all regardless of width — the paper's own "every dataset materially
  harmed at k=1" saturation — so width cannot discriminate there. Suggested framing: report all four; note
  the effect emerges from k=2 and saturates at k=1.

## Deliverables (flat zip, script inside)
`RESULTS_p5_across_budgets.md` · `p5_width_across_budgets.csv` (per-budget ρ/p/CI/n) ·
`p5_width_across_budgets.json` (headline) · `p5_width_rows.csv` (per-dataset harm at each budget) ·
`compute_p5_across_budgets.py` · `DONE.md` · `MANIFEST.sha256`.
