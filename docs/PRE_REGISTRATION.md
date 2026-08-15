# Pre-registration — feature-reduction calibration & fairness audit

> **Dated addendum, 2026-08-11 (revision round; original text below is unchanged).**
> This document is a historical record and is deliberately never edited. Two kinds of
> divergence between it and the study as published exist and are disclosed here rather than
> papered over. (1) *Scope growth before submission:* the dataset list grew from the five
> named in §Datasets to twelve, additional outcomes (net benefit, conformal set size,
> selective ECE, net-benefit and coverage gaps) were added, and the venue changed from the
> journals named in §Datasets to Scientific Reports. The frozen elements — the independent
> variable, the reference comparison, the pairing, the Holm+bootstrap materiality rule, and
> the leakage firewall — were applied unchanged to every addition. (2) *Revision-round
> additions (2026-08), in response to peer review:* an exact-$k$ budget arm ($k\in\{1,2,4,8\}$,
> its own Holm family), the full Diabetes-130 cohort in place of the 6,000-encounter
> subsample, a retained-$k$ reanalysis of the cross-dataset screen, and a per-patient
> decision-flip analysis at a pre-declared threshold (mammographic mass, $t=0.10$, cell fixed
> in `config/analysis.json` before any flip count was computed). These are POST-registration
> analyses and the manuscript labels them as such; the pre-registered decision rule itself
> was not altered at any point.

Frozen before the validated (REPS=30) results were read. This fixes the outcomes, the
independent variable, the comparison, and the decision rule so the trade-off direction
is not chosen post hoc. No sign of the effect is pre-committed: degradation, no change,
or improvement are all reportable.

## Question

On clinical tabular data, as feature-reduction aggressiveness increases, does
**probability calibration** (ECE, Brier) degrade and do **subgroup-fairness gaps** widen,
even when headline discrimination (AUROC) appears stable? And does **selective prediction**
(abstention) buy back reliability (lower area-under-risk-coverage, AURC)?

## Independent variable

`frac` = fraction of features retained, swept over {1.0, 0.75, 0.5, 0.33, 0.25}.
`frac = 1.0` (all features) is the reference baseline. Feature reduction uses three
standard, published strategies (filter by mutual information; random-forest importance;
L1-logistic), not a novel optimiser.

## Outcomes (frozen)

Per cell `(dataset, method, classifier, frac, rep)`, on pooled out-of-fold probabilities:

- Discrimination: accuracy, AUROC.
- Calibration: ECE (15-bin), Brier score.
- Selective prediction: AURC (area under risk-coverage; confidence = `|p-0.5|`; lower better).
- Subgroup fairness gaps: max-min AUROC across protected groups; max-min ECE across groups.

Protected attribute: as each dataset permits (Cleveland: sex).

## Comparison and decision rule

Each non-reference `frac` is compared to `frac = 1.0`, **paired across reps** (the seed does
not depend on `frac`, so every reduction level shares the same cross-validation split within
a rep). For each `(dataset, method, classifier, outcome)` family across the reduction levels:

- paired difference `delta = mean(metric@frac - metric@full)`, paired Cohen's d;
- two-sided Wilcoxon signed-rank p-value, **Holm step-down corrected (R3)** within the family;
- a 5000-resample percentile bootstrap CI on the paired difference (R12).

A reduction level is declared to **materially change** an outcome iff `p_holm < 0.05` AND the
bootstrap CI on the paired difference excludes zero. A finding that aggressive reduction
**does not** harm calibration/fairness is equally reportable.

## Leakage firewall

Imputation, feature reduction, scaling, and classifier fitting all happen **inside** each
cross-validation fold, using training-fold statistics only; the test fold is never seen
during selection or fitting. Enforced by the test suite (a shuffled-label run must yield
AUROC ~ 0.5).

## Reproducibility

REPS = 30 per cell (R4); per-cell deterministic seeds from a master seed (R5); the
`config/calibration.json` content hash is embedded in every results CSV (R6); all numbers
derive from one canonical aggregator (R2); raw per-cell rows are gitignored, the summary CSV
is committed; results are tagged `validated`/`provisional` (N14).

## Datasets

Cleveland (first), then Pima, ILPD, WDBC, Heart-Failure (public UCI tabular). External
validity across structurally different corpora; venue: Journal of Biomedical Informatics or
Computers in Biology & Medicine (subscription route, no APC).
