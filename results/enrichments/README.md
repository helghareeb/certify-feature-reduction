# Enrichment experiments

Twenty-four controls and extensions run for the revised manuscript, beyond the main grid in
`results/summary*.csv`. Every folder has a row in the table below, and every folder holds its own
`MANIFEST.sha256`.

Results that came out against the hypothesis that motivated them are marked 🔻.

| folder | question | outcome | paper |
|---|---|---|---|
| `00_environment_gate` | Does the environment reproduce the pinned library versions and test suite? | Pass | Methods |
| `01_ece_bin_sensitivity` | 15 equal-width ECE bins were fixed *a priori* and never swept. Is any calibration conclusion an artefact of that? | Bin-count-robust across {5,10,15,20,30,50} bins under equal-width **and** equal-frequency binning; one of 72 cells changes sign, material at none of the six counts | Limitations |
| `02_high_dimensional_arm` | Does the account extend to $p \gg 44$? Four datasets, $p = 279$–$22{,}283$ | 🔻 Harm is **not** monotone in $p$ ($-0.278$, $-0.043$, $-0.298$, $-0.159$ at $k=1$) | High-dimensional arm |
| `03_recalibrators_beta_temperature` | Two further recalibrators — temperature (1 parameter), beta (3) | ECE $-8\,\%$ and $-28\,\%$; AURC $-3\,\%$ and $+0.6\,\%$. Beta is decisive: flexible, parametric, moves calibration error without moving selective reliability | Recalibration |
| `04_ensemble_disagreement_confidence` | Can per-tree disagreement serve as a probability-independent confidence? | 🔻 **No, structurally.** Pooled Spearman with $\lvert p-0.5\rvert$ is $-0.991$ — a forest disagrees most near its own decision boundary | Limitations |
| `05_gradient_boosting_bin_sweep` | The bin sweep excluded the one learner whose raw calibration is not poor | Reduction *materially improves* its calibration error while its selective-reliability penalty is $+0.028$ | Recalibration |
| `06_distance_to_support_confidence` | Limitations conceded a probability-independent confidence "would require … which we did not run". This runs it | **Two-thirds of the measured selective-reliability harm is a property of the probability scale** ($+0.0334 \to +0.0116$). The surviving third holds at $p = 7\times10^{-103}$ | Discussion, Abstract |
| `07_sample_size_vs_width` | Is the high-dimensional harm about $n/p$? | 🔻 No. Holding $p=279$ and cutting $n$ leaves the penalty unchanged | High-dimensional arm |
| `08_cross_dataset_correlates` | Is cohort size the hidden variable? | 🔻 Dismissed — and *negative* once $p$ is partialled out | What predicts the harm |
| `09_signal_concentration` | Does a scalar concentration index order the harm? | 🔻 **Refuted.** The predicted ordering fails under mutual information and random-forest importance, and once corrected for width it is reproduced **zero** times across the 45 combinations of statistic, ranker and correction. Only the prostate-versus-arcene contrast survives | High-dimensional arm |
| `09_signal_concentration_16ds` | The same measurement extended to 16 datasets, adding glioma and the readmission cohort | Supersedes the 14-dataset delivery for coverage. Carries a verified transport hash rather than an author-signed content manifest, and says so | High-dimensional arm |
| `10_independence_vs_sample_size` | Does the independence in `06` decay with $n$? | No trend ($\rho = -0.08$). The paper reports the **unweighted mean 0.27**, not the pooled 0.40 | Discussion |
| `10b_cross_axis_coherence` | Are the five reliability axes one scale or several? | Two coherent groups: ordering-based axes agree (AURC ↔ conformal $+0.89$), scale-based axes agree (ECE ↔ selective-ECE $+0.97$), the groups are near-independent ($+0.30$) | Discussion |
| `11_recalibrator_flexibility_ladder` | "You did not try a flexible enough recalibrator" | ECE recovery rises **strictly monotonically** with flexibility ($+1.00$); selective-reliability recovery does not ($-0.90$) | Recalibration |
| `12_probe_injection_dose_response` | Pre-registered **causal** test: inject pure-noise features at fixed budget | 🔻 **The registered prediction failed.** Dilution *lowered* the penalty or reversed it. Reduction defends against noise padding | High-dimensional arm |
| `12b_kept_set_composition` | Does composition matter at a fixed budget? | 🔴 **Superseded, not cited.** The kept set was selected using the labels outside the cross-validation, which biases the result in the direction measured. Kept as the record of the defect; re-run leakage-free in `12c` | *(not cited)* |
| `12c_kept_set_composition_paired` | The same question, paired within folds and leakage-free | The rise survives: $+0.025$ $[0.022, 0.028]$ at the top-100 rung to $+0.091$ $[0.083, 0.100]$ with all 10,000 available, monotone, extremes disjoint. 900 cells | High-dimensional arm |
| `13_safe_budget_diagnostic` | Does the concentration curve work as a safe-budget proxy? (pre-registered thresholds) | 🔻 Fails as a predictor: 59 % agreement, sensitivity $1.00$, specificity $0.15$. The "no proxy certifies a budget" conclusion stands | Certificates |
| `14_surviving_penalty_localisation` | Is the surviving probability-independent penalty the same phenomenon as the distributed-signal account? | 🔻 Null on all three predictors. Two findings, not one mechanism | Limitations |
| `15_matched_absolute_budget` | The retained count and $p$ are collinear because $k = 0.25p$. What happens at matched $k$? | Harm still rises with width at every budget from $k=2$ up ($\rho = +0.60, +0.69, +0.77$ at $k = 2, 4, 8$ on all twelve, eleven and nine qualifying datasets), so the retained-count association is partly collinearity. Not significant at $k=1$, where every dataset is harmed regardless of width | What predicts the harm |
| `16_high_dimensional_fifth_dataset` | Does a fifth, wider dataset change the high-dimensional picture? | No, and it sharpens it: smk-can-187 ($p=19{,}993$) is *less* harmed at $k=1$ ($-0.176$) than arcene at $p=10{,}000$ ($-0.298$), so higher dimensionality is not safer. Concentration orders it differently under different rankers | High-dimensional arm |
| `17_combined_confidence` | Can a pre-registered combination of confidence signals mitigate the surviving selective-reliability harm? | Partly, and the counter-result is reported beside it: the combination removes $48.3\,\%$ of the AURC penalty (positive on all twelve, CIs disjoint), but does **not** improve selective net benefit. 2,160 cells on the full cohort | Limitations |

| `18_decision_flip_decomposition` | Which way do the decision flips go, and does that depend on the threshold? | Both, and it matters: at the pre-registered $10\,\%$ biopsy threshold 188 of 203 flips are *new* referrals, not withdrawals, and the direction inverts by $t=0.30$ where 93 malignant patients lose a biopsy recommendation. The reduced model emits 29 distinct risks against the full model's 846, which is what sets the direction | Worked example |
| `19_dataset_level_inference` | Do the headline claims survive a test that assumes nothing about repetition count? | Yes for five axes, no for two: an exact sign test over the twelve dataset means gives 12/12 for selective reliability and discrimination ($p=0.0002$), 11/12 for net benefit, conformal set size and Brier, and 8/12 for the two calibration axes ($p=0.19$) --- the same split the cell counts give | Results, Statistics |
| `20_metric_diagnostics` | Do the outcome metrics measure what the study says they measure at aggressive budgets? | Three answers. (i) A calibration error can fall because a model collapses onto the base rate: on the readmission cohort at one feature ECE falls $10.2\times$ while resolution falls $15.7\times$, the prediction spread $4.1\times$ and attainable risks from 101,259 to 16 --- so ECE understates the harm, and Brier, which carries the resolution term, rises. (ii) The conformal estimator is transductive rather than split, and *overstates* the paired set-size penalty by $5\,\%$ ($+0.272$ against a split's $+0.259$). (iii) AURC breaks confidence ties on row order; over 2,000 permutations the $95\,\%$ interval is $3$--$5\,\%$ of the matched-arm penalty | Outcomes, Results, Threats |
| `21_net_benefit_default_strategies` | Is the net-benefit axis measured where a model is needed at all? | On ten of twelve datasets, yes, and by a wide margin (smallest $+0.111$ over treat-all). On ILPD ($\pi=0.714$) and SPECTF ($\pi=0.794$) the evaluated range $t\in[0.05,0.5]$ lies entirely below the prevalence and the model never beats treating everyone. 11 of the 80 materially degraded cells sit there, leaving 69 --- a restriction of scope rather than a change of result | Outcomes, Results |

## Verified continuously, not once

Each folder's `MANIFEST.sha256` and the tree-level `results/MANIFEST.sha256` are checked on every
push by [`.github/workflows/verify.yml`](../../.github/workflows/verify.yml), together with the
provenance gate that refuses a committed result with no committed code behind it. The workflow also
regenerates the worked clinical example from the committed caches and asserts its published values,
so the number a reader is most likely to check cannot drift silently.

## How to read these folders

- `*.csv` — the numbers. Every committed column is declared in `paper/MANIFEST.toml`, either as cited
  in the manuscript or as out of scope **with a written reason**.
- `*.json` — machine-readable summaries carrying the headline statistics, so a claim in the prose can
  be checked against an artifact rather than only read.
- `RESULTS_*.md` — the report written when each experiment landed, including its pre-ruled outcomes.
- `PRESPEC_*.md` — pre-registrations, committed before the corresponding numbers were computed.
- `MANIFEST.sha256` — SHA-256 for every file in the folder.
- `calibration_*.json` — the configuration that produced the run, so the `calibration_sha256` stamped
  into each results file resolves to a file you can hash yourself.

The code that produced these is in `experiments/enrichments/`, with the frozen library copy it ran
against.
