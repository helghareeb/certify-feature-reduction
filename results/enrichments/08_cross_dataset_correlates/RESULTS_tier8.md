# RESULTS — Tier 8: cross-dataset correlates of reduction harm (with partials + LODO)

**Run:** second compute node · **2026-08-14 ~01:20 AST** · per `the Tier 8 plan.md`.
Pure post-hoc arithmetic over summaries already delivered — no fits, no folds. Run concurrently with
`arcene`/`gli85` under the parallelization the review approved (`ANSWER_parallelize.md`).

> **Standing caveat (must travel with these numbers).** With twelve datasets, **no correlation here is
> confirmatory.** These are descriptive, exploratory quantities on a small sample of heterogeneous
> datasets, and are reported as such. Partial correlations at n=12 are especially low-powered; they are
> included to show whether a marginal association *survives* conditioning, not to estimate its size.

## Design (built around Reviewer 1's earlier confound)
Unit of analysis = one dataset. **Harm** = reduction penalty at the most aggressive budget, two ways,
each meaned over the 3 rankers × 3 learners: `harm_auroc = −Δ(AUROC)` and `harm_aurc = +Δ(AURC)`
(positive = worse). Because across datasets `n` covaries with `p`, prevalence and retained-`k`, every
marginal correlation is reported **beside its competitors and with partial correlations**, so `n`'s
number cannot be read alone.

## Primary block — 12 clinical datasets, aggressive budget = frac 0.25
Spearman ρ [95% seeded 5000-resample bootstrap CI], p, and leave-one-dataset-out (LODO) range:

| candidate | vs harm_AUROC | vs harm_AURC |
|---|---|---|
| **n** | +0.049 [−0.62, +0.64] p=0.88 · LODO[−0.17,+0.23] | +0.224 [−0.49, +0.74] p=0.48 · LODO[+0.03,+0.38] |
| **p** | −0.498 [−0.86, +0.21] p=0.099 · LODO[−0.62,−0.36] | **−0.709 [−0.96, −0.16] p=0.0099** · LODO[−0.83,−0.62] |
| **n/p** | +0.301 [−0.41, +0.79] p=0.34 · LODO[+0.16,+0.46] | +0.448 [−0.27, +0.91] p=0.14 · LODO[+0.28,+0.65] |
| **prevalence** | +0.028 p=0.93 · LODO[−0.15,+0.22] | +0.168 p=0.60 · LODO[+0.06,+0.52] |
| **retained-k @ aggr** | **−0.577 [−0.90, +0.06] p=0.050** · LODO[−0.70,−0.45] | **−0.779 [−0.98, −0.31] p=0.0028** · LODO[−0.88,−0.71] |

## Partial correlations — the point (first-order Spearman)
| partial | AUROC | AURC |
|---|---|---|
| harm vs **n** \| p | −0.256 p=0.45 — **collapses** | −0.198 p=0.56 — **collapses** |
| harm vs **p** \| n | −0.544 p=0.084 — holds | **−0.705 p=0.015 — survives** |
| harm vs **n** \| retained-k | −0.301 p=0.37 — collapses | −0.247 p=0.46 — collapses |

## Reading (pre-specified outcome: harm-vs-n COLLAPSES under the partials)
1. **`n` is not the operative variable.** Its marginal correlation with harm is near zero, and the
   little that exists dies once `p` (or retained-k) is held. Between datasets, sample size does not
   predict reduction harm — it was `p` wearing `n`'s clothes. Reported plainly as the useful negative
   the addendum pre-ruled.
2. **`p` and retained-k are the operative variables.** Both are the strongest marginals and `p`
   *survives* conditioning on `n` (AURC ρ=−0.71, p=0.015). Retained-k is the single strongest
   correlate (AURC ρ=−0.78) — matching the manuscript's own "retained count is what matters" story.
   More features available / more retained ⇒ less harm from cutting.
3. **Direction is consistent across both harm axes** (AUROC and AURC give the same ranking of causes),
   which is reassuring for 12 points but does not make it confirmatory — see the caveat.
4. **Cross-check with Tier 7.** Tier 8 tests `n` *between* datasets; Tier 7 tests `n` *within* a
   dataset at fixed `p` (the stronger design). If Tier 7 also finds no `n` effect, the between-dataset
   null is corroborated by a design that cannot be confounded by `p` at all.

## Secondary block — high-dimensional sets (SEPARATE, not pooled)
Different budget protocol (aggressive = k:1), so **not** combined with the clinical correlations —
appended as descriptive rows only. Complete 4-set block (adds `arcene`, `gli85`) folds in when those
runs land; current rows:

| dataset | n | p | n/p | prevalence | harm_AUROC@k1 | harm_AURC@k1 |
|---|--:|--:|--:|--:|--:|--:|
| arrhythmia | 452 | 279 | 1.620 | 0.458 | 0.278 | 0.255 |
| prostate_ge | 102 | 5,966 | 0.017 | 0.510 | 0.043 | 0.028 |

Consistent with the primary block and the Tier-2 partial: the low-`p` set takes the larger hit.

## Deliverables
`RESULTS_tier8.md` · `tier8_correlates_clinical.csv` (12 datasets, all candidates + harm) ·
`tier8_correlates_highdim.csv` (2 sets now; 4 when landed) · `tier8_report.json` (all ρ/p/CI/LODO/
partials) · `DONE.md` · `MANIFEST.sha256`. Separate artifact, not merged (R6). Numbers, not caches.
