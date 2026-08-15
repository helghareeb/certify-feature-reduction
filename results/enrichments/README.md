# Enrichment experiments

Nineteen controls and extensions run for the revised manuscript, beyond the main grid in
`results/summary*.csv`. Each folder holds its `MANIFEST.sha256`; all 89 entries verify.

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
| `09_signal_concentration` `09_..._16ds` | Does a scalar concentration index order the harm? | 🔻 **Refuted.** Holds 2 of 9 ranker × statistic tests, and **0 of 21** once corrected for width | High-dimensional arm |
| `10_independence_vs_sample_size` | Does the independence in `06` decay with $n$? | No trend ($\rho = -0.08$). The paper reports the **unweighted mean 0.27**, not the pooled 0.40 | Discussion |
| `10b_cross_axis_coherence` | Are the five reliability axes one scale or several? | Two coherent groups: ordering-based axes agree (AURC ↔ conformal $+0.89$), scale-based axes agree (ECE ↔ selective-ECE $+0.97$), the groups are near-independent ($+0.30$) | Discussion |
| `11_recalibrator_flexibility_ladder` | "You did not try a flexible enough recalibrator" | ECE recovery rises **strictly monotonically** with flexibility ($+1.00$); selective-reliability recovery does not ($-0.90$) | Recalibration |
| `12_probe_injection_dose_response` | Pre-registered **causal** test: inject pure-noise features at fixed budget | 🔻 **The registered prediction failed.** Dilution *lowered* the penalty or reversed it. Reduction defends against noise padding | High-dimensional arm |
| `12b_kept_set_composition` | Does composition matter at a fixed budget? | 🔴 **Not cited.** The kept set was selected using the labels outside the cross-validation, biasing the result in the direction measured. Re-running leakage-free | *(not cited)* |
| `13_safe_budget_diagnostic` | Does the concentration curve work as a safe-budget proxy? (pre-registered thresholds) | 🔻 Fails as a predictor: 59 % agreement, sensitivity $1.00$, specificity $0.15$. The "no proxy certifies a budget" conclusion stands | Certificates |
| `14_surviving_penalty_localisation` | Is the surviving probability-independent penalty the same phenomenon as the distributed-signal account? | 🔻 Null on all three predictors. Two findings, not one mechanism | Limitations |
| `15_matched_absolute_budget` | The retained count and $p$ are collinear because $k = 0.25p$. At matched $k=8$? | Harm still rises with width ($\rho = +0.77$), so the retained-count association is partly collinearity | What predicts the harm |

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
