# RESULTS — Tier 9: signal concentration as the mechanism behind the arcene/prostate_ge dissociation

**Run:** second compute node · **2026-08-14 ~03:10 AST** · per `the Tier 9 plan.md`.
Ran low-priority beside `gli85`/Tier 7. **14/16 datasets** here (diabetes130 concentration + `gli85`
fold in when ready; neither changes the decisive pair, and the correlation is already flat).

## Method note — rankings were NOT cached
Only OOF probabilities are cached; `reduction.rank()` returns order, not scores. So the ranker **scores**
were recomputed exactly as `nsclinfs.reduction` does (mutual_info_classif scores / 80-tree RF-importance
ranking fit / |L1-logit coef|), on rep-0 folds, normalised to sum 1 and averaged over the 5 folds.
Concentration is reported **per (dataset, ranker)** — never averaged across rankers. Index = **Gini**
of the normalised score distribution (consistent throughout), plus cumulative top-k share.

## T9.2 — the decisive pair (this is the result)
Near-identical n/p (prostate_ge 0.017 vs arcene 0.020), opposite reduction outcomes. Does concentration
differ in the predicted direction — prostate_ge concentrated, arcene diffuse? **Yes, on every ranker:**

| ranker | quantity | **prostate_ge** (safe) | **arcene** (harmful) | direction |
|---|---|--:|--:|:--:|
| mutual_info | top-64 share | 0.061 | 0.028 | concentrated ✓ |
| mutual_info | Gini | 0.513 | 0.487 | ✓ |
| rf_importance | top-8 share | 0.103 | 0.029 | ✓ |
| rf_importance | top-64 share | **0.382** | **0.143** | ✓ |
| rf_importance | Gini | 0.908 | 0.834 | ✓ |
| l1_logistic | top-8 share | **0.660** | **0.150** | ✓ |
| l1_logistic | top-64 share | 0.996 | 0.526 | ✓ |
| l1_logistic | Gini | 0.997 | 0.982 | ✓ |

prostate_ge concentrates its predictive signal in far fewer features — RF-importance puts 38% of the
mass in the top 64 features (arcene 14%); L1 puts 66% in the top 8 (arcene 15%). So selecting a small k
**preserves** prostate_ge's signal but **discards** much of arcene's diffuse signal. **The mechanism in
the arcene flag is now measured, not inferred**, and it points the predicted way — the strong outcome
for the pair. The gap is largest for `rf_importance` and `l1_logistic`, the rankers that actually drove
the selection; `mutual_info` shows the same direction more weakly.

## T9.3 — the correlation does NOT generalise (report plainly)
Concentration (Gini) vs harm (AUROC penalty at the aggressive budget) across **14 datasets** (12 clinical
+ arrhythmia/prostate_ge/arcene, **two labelled blocks, not pooled into one trend**):

| ranker | Spearman ρ | 95% boot CI | p | LODO | partial \| p | partial \| retained-k |
|---|--:|---|--:|---|--:|--:|
| mutual_info | −0.002 | [−0.61, +0.60] | 0.99 | [−0.12, +0.25] | −0.025 | −0.228 |
| rf_importance | +0.033 | [−0.59, +0.59] | 0.91 | [−0.17, +0.14] | −0.033 | −0.051 |
| l1_logistic | −0.064 | [−0.65, +0.54] | 0.83 | [−0.29, +0.06] | −0.147 | −0.211 |

**Flat at every ranker**, with CIs spanning ±0.6 and nothing to survive under conditioning. A single
concentration index does **not** predict reduction harm across heterogeneous datasets — so concentration
is **not** the general pre-reduction risk proxy we hoped for. This is the second pre-specified outcome: the
matched pair explains its dissociation, the correlation simply does not generalise at this many points.

> **Caveat (in my words).** These sixteen (here fourteen) datasets are a small, heterogeneous sample.
> The correlation is descriptive and exploratory, not confirmatory. The load-bearing evidence is the
> **controlled pair**, not the correlation — as in §4.7's Haberman/SPECTF dissociation, where the pair
> carries the claim and the correlation is only context.

## T9.4 — probes: skipped honestly
arcene as distributed (`arcene.mat`) contains only `{X, Y}` — **no probe/feature labels**. The NIPS-2003
injected-probe fraction is therefore not computable from what we have, and was **not** reconstructed or
guessed. Skipped.

## Bottom line
The high-dimensional arm is **not** a p-trend (arcene flag) and **not** an n/p-trend (matched pair). The
operative difference between the safe and harmful high-p sets is **signal concentration**, measured and
in the predicted direction — but it works as a *mechanism for the specific pair*, not as a *general
predictor* (null correlation). Both facts are reported; neither is smoothed.

## Deliverables
`RESULTS_tier9.md` · `tier9_concentration.csv` (Gini + top-k shares, per dataset×ranker) ·
`tier9_correlation.json` (ρ/CI/LODO/partials per ranker) · `DONE.md` · `MANIFEST.sha256`.
Separate artifact, not merged (R6). diabetes130 + gli85 fold in on completion.
