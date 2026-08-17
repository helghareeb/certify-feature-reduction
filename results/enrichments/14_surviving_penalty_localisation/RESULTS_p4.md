# RESULTS — P4: does the surviving -d penalty live in the concentrated datasets? (null)

**Run:** second compute node · **2026-08-16 00:05 AST** · approved enrichment P4 (low priority),
cache-only. Tests whether the ~35% of the AURC reduction penalty that SURVIVES the X-only confidence
(-d, Tier 6 T6.3, per-dataset penalty_d) is concentrated in the datasets with concentrated signal
(Tier 9 Gini) or few retained features (Tier 8) -- i.e. whether Tiers 6 and 9 are one story.

## Result -- NO localization (null at 12 datasets)
| Spearman(surviving penalty_d, X) | rho | p |
|---|--:|--:|
| X = Gini (rf_importance) | +0.210 | 0.513 |
| X = retained-k @ aggressive | -0.160 | 0.619 |
| X = p | -0.126 | 0.696 |

All null. The surviving selective-reliability signal is **not** preferentially located in the
concentrated (or low-retained-k, or low-p) datasets -- it is spread across the panel without a
detectable relationship to concentration.

## Reading (pre-ruled: report plainly either way)
Tiers 6 and 9 do **not** unify via this link at 12 datasets: the fact that ~35% of the penalty is
probability-independent (Tier 6) and the fact that reduction harm is about distributed signal (Tier 9/P1)
are, on this evidence, **two separate findings, not one mechanism.** Reported as the honest negative it
is; nothing in the paper depends on them being the same story, and at n=12 this test is low-powered
(descriptive, not confirmatory).

## Deliverables
`RESULTS_p4.md` · `p4_surviving_vs_concentration.csv` (per-dataset penalty_d, Gini, retained-k, p) ·
`p4_summary.json` · `DONE.md` · `MANIFEST.sha256`.
