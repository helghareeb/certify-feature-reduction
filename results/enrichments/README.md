# Enrichment experiments

Thirteen controls and extensions run for the revised manuscript, beyond the main grid in
`results/summary*.csv`. Each folder holds the numbers exactly as computed — no file here has been
edited since it was produced. Integrity for the whole `results/` tree is in `results/MANIFEST.sha256`.

Several of these returned **against** the hypothesis that motivated them. Those are marked 🔻 and are
reported in the paper as prominently as the confirmations, because a control that can only agree with
you is not a control.

| folder | question | outcome | paper |
|---|---|---|---|
| `00_environment_gate` | Does the secondary compute node reproduce the pinned environment and test suite before anything is trusted from it? | Pass — environment gate cleared prior to any result | Methods |
| `01_ece_bin_sensitivity` | The manuscript fixed 15 equal-width ECE bins *a priori* and had never swept them. Is any calibration conclusion an artefact of that choice? | Bin-count-robust across {5,10,15,20,30,50} bins under equal-width **and** equal-frequency binning; exactly one of 72 cells changes sign, material at none of the six counts, magnitude ≤ 0.002 | Limitations |
| `02_high_dimensional_arm` | Does the account extend to $p \gg 44$, where reduction is most often applied? Four biomedical datasets, $p = 279$–$22{,}283$, absolute-$k$ budgets | 🔻 Harm is **not** monotone in $p$ ($-0.278$, $-0.043$, $-0.298$, $-0.159$ at $k=1$) | High-dimensional arm |
| `03_recalibrators_beta_temperature` | Two further post-hoc recalibrators — temperature (1 parameter) and beta (3 parameters) — under the same leakage-safe protocol | ECE $-8\,\%$ and $-28\,\%$; AURC $-3\,\%$ and $+0.6\,\%$; net benefit $0\,\%$ and $+0.8\,\%$. Beta is the decisive case: flexible, parametric, and it moves calibration error without moving selective reliability | Recalibration |
| `04_ensemble_disagreement_confidence` | Can per-tree disagreement serve as a confidence signal independent of the predicted probability? | 🔻 **No, structurally.** Pooled Spearman with $\lvert p-0.5\rvert$ is $-0.991$ over 11,180 out-of-fold points, $\geq 0.96$ on every dataset — a forest disagrees most near its own decision boundary | Limitations |
| `05_gradient_boosting_bin_sweep` | The bin sweep excluded gradient boosting, the one learner whose raw calibration is not poor. Does the dissociation hold without that confound? | Reduction *materially improves* its calibration error while its selective-reliability penalty is simultaneously $+0.028$ | Recalibration |
| `06_distance_to_support_confidence` | The submitted Limitations conceded that a probability-independent confidence "would require … which we did not run". This runs it: mean distance to the 10 nearest training neighbours in feature space | **Two-thirds of the measured selective-reliability harm is a property of the probability scale** (AURC penalty $+0.0334 \to +0.0116$). The surviving third holds at $p = 7\times10^{-103}$ | Discussion, Abstract |
| `07_sample_size_vs_width` | Is the high-dimensional harm really about $n/p$? Subsample $n$ with $p$ held fixed | 🔻 No. Holding $p = 279$ and cutting $n$ to reach $n/p \approx 0.36$ leaves the penalty unchanged | High-dimensional arm |
| `08_cross_dataset_correlates` | Is cohort size the hidden variable behind the harm? | 🔻 Dismissed. Raw $\rho(n,\text{harm}) = +0.05/+0.22$, and *negative* once $p$ is partialled out; the retained count dominates at $\rho = -0.78$ | What predicts the harm |
| `09_signal_concentration` `09_..._16ds` | Does a scalar concentration index (Gini, top-$k$ share) order the harm across the high-dimensional datasets? | 🔻 **Refuted, and the refutation is in the paper.** The ordering holds 2 of 9 ranker × statistic tests, and **0 of 21** once corrected for width. `gini` disagrees with the claim under every ranker | High-dimensional arm |
| `10_independence_vs_sample_size` | The pooled independence figure for `06` is dominated by one 101k-encounter cohort. Does independence decay with $n$? | No $n$-trend ($\rho = -0.08$, $p = 0.80$). The paper therefore reports the **unweighted per-dataset mean 0.27**, not the pooled 0.40 | Discussion |
| `11_recalibrator_flexibility_ladder` | "You did not try a flexible enough recalibrator." Order all five by free parameters on one matched grid | ECE recovery rises **strictly monotonically** with flexibility (Spearman $+1.00$); selective-reliability recovery does not ($\rho = -0.90$, $\leq 3.1\,\%$ of baseline) | Recalibration |
| `12_probe_injection_dose_response` | A pre-registered **causal** test: inject pure-noise features while holding rows, true features, folds and the absolute budget fixed. Prediction registered before computing (`PRESPEC_p1.md`) | 🔻 **The registered prediction failed.** Dilution *lowered* the penalty (cleveland $+0.054 \to +0.006$, intervals disjoint) or reversed it (spectf $+0.004 \to -0.037$). Reduction defends against noise padding | High-dimensional arm |

## How to read these folders

- `*.csv` — the numbers. Column meanings for every committed column are declared in
  `paper/MANIFEST.toml`, either as cited in the manuscript or as out of scope **with a reason**.
- `*.json` — machine-readable summaries, including the headline statistics so they can be checked
  against the prose rather than only read in it.
- `PRESPEC_*.md` — pre-registrations, committed before the corresponding numbers were computed.
- `calibration_*.json` — the configuration that produced the run, so the `calibration_sha256` stamped
  in each results file resolves to a file you can hash yourself.

The narrative delivery reports that accompanied these results were internal working correspondence —
run queues, scheduling, status notes — and are not part of the scientific record. Everything they
concluded is in the manuscript, and everything they measured is in the files here.
