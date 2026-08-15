# RESPONSE — point-by-point ledger (SR revision, submission 2650209c)

> Working ledger per the program's `ADD-response` rule: **every reviewer point maps to a change
> and a commit id** (or a decline with a stated reason). The polished response-to-reviewers
> letter is generated FROM this file at packaging time (separate file, no "Dear…" salutation).
> Status vocab: `planned · in-progress · done(<commit>) · declined(<reason>)`.

## Editor (Pijush Samui — no itemized comments)

| id | point | change | status |
|---|---|---|---|
| E.1 | "ensure the results are accurately reported, any overstated conclusions are rewritten and the limitations of the work fully explained" | Blanket pass folded into every R1/R2 item below + the beyond-reviewer audit (k-floor disclosure, monotonicity scoping, ρ=−0.73 requalification, explicit p≫44 exclusion in Methods AND Limitations) | done(1e3b1e8) |

## Reviewer 1

| id | point | change | status |
|---|---|---|---|
| R1.1 | ρ=−0.73 confounded by the max(1,round(frac·p)) floor; re-relate harm to absolute retained-k / matched-k | Tier 1: full k-based reanalysis (harm vs k_min, k=1-collapse indicator, ρ excluding the two floor datasets, harm-vs-k curves at matched k across all budgets) — zero new fits, from the released summary. Tier 2: NEW exact-k budget arm k∈{1,2,4,8} for every dataset (paired within-rep, Holm families isolated per budget type) — the decisive separation the reviewer asks for. Methods now states the floor rule and its consequence table explicitly. The screening criterion is restated in whichever form survives (absolute-k rule vs p-rule), with both correlations reported. | done(1e3b1e8) |
| R1.2 | precedent for FS on low-dimensional medical data + explicit p≫44 exclusion | Related-work paragraph added: chicco2020machine is itself a 2-of-12-feature reduction on our heart-failure cohort (the practice, on our own data, in the harmed regime), plus Cleveland/Pima compact-model precedents; explicit BOLD out-of-scope statement for p≫44 in Limitations; budget-rule floor disclosed in Methods §3.2. | done(fb5c064) |
| R1.3 | worked patient-level decision-flip example at a specific clinical threshold | New worked example: mammographic mass, biopsy decision at t=0.10 (BI-RADS 4b boundary; sensitivity at t∈{0.05,0.15}); per-patient table (p_full vs p_reduced, decision flip, flip rate over 30 paired reps) + per-threshold decision-curve figure (full vs reduced vs treat-all/none). Secondary (supplementary): full Diabetes-130 cohort, t=0.10 — absolute count of patients whose enrollment decision flips. Backed by newly persisted per-patient/per-threshold caches, committed. | done(1e3b1e8) |
| R1.4 | full Diabetes-130 cohort, at least for the headline | Over-delivered: the ENTIRE grid (all rankers × learners × budgets × 30 reps) re-run on the full cohort (~101,763 encounters, post gender-filter); the 6,000-row arm is retained only as a subsample-agreement robustness table (corrected to joint outcome×race stratification). | done(1e3b1e8) |
| R1.5 | code repository must be available for reviewer inspection | The repository is made PUBLIC on the day this revision is submitted (author's decision) — not merely on request, and not deferred to acceptance. Code Availability rewritten accordingly; repo release-audited (data fetch script + pinned manifest, license, citation metadata, cold-start reproduction instructions). | in-progress (flip on resubmission day) |

## Beyond the requested changes (author-directed enrichments, approved 2026-08-11)

| id | addition | status |
|---|---|---|
| E1 | **Minimum certified-safe budget table** — smallest retained-k per dataset at which no reliability axis is materially worse (turns the audit into a usable certificate; completes R1.1's line of thought) | done(1e3b1e8) — only wdbc certifies (k=22/30); table in manuscript |
| E2 | **Screen robustness** — leave-one-dataset-out ρ (all-negative on v1 mechanics) + seeded 5000-resample bootstrap CI on both correlations | done(1e3b1e8) — LODO all-negative, bootstrap CIs exclude 0 |
| E3 | **Population flip-rate distribution** — CDF over all patients, both worked-example cells | done(1e3b1e8) |
| E4 | **Race-split decision flips** on the full Diabetes-130 cohort at t=0.10 (who bears the instability) | done(1e3b1e8) |
| E5 | **Reliability diagrams** full-vs-reduced for the primary cell, from cached probabilities | done(1e3b1e8) |
| E6 | **Strack et al. 2014 dataset citation** + external-range anchor sentence + boxed six-step practitioner checklist in Discussion | done(1e3b1e8) |
| E7 | **Ranking-stability analysis** — Jaccard of top-k selections across 150 fold-rankings per dataset×ranker, correlated with harm (the mechanism question) | done(1e3b1e8) — honest null (rho=+0.14, p=0.66), reported as figure |
| E8 | **Recalibration control extended to all three rankers** — the submitted version ran the {none, Platt, isotonic} depth control on the mutual-information ranker only and stated the restriction as a limitation, expecting the dissociation to hold for the others. That expectation is now measured: 87/87 shards, 12 datasets × 3 rankers × 3 learners × 3 depths, 6,966 rows | done(1ab9e06) — **dissociation confirmed for all three rankers**; ECE recovers (random forest +0.0215 → +0.0020 Platt), AURC persists (+0.0317 → +0.0313), materially worse in 95–96 of 108 cells under either recalibrator. The limitation is deleted, not defended. Two things the single-ranker version could not say: under random-forest importance recalibration makes AURC **worse** (+0.0399 → +0.0426), and the submitted ranker was the **conservative** choice, so the effect is not an artefact of how features were ranked |
| E9 | **ECE bin-count sensitivity sweep** — §Limitations previously stated that ECE is binning-dependent, that 15 equal-width bins were fixed a priori, and that no sensitivity sweep had been run. Swept {5,10,15,20,30,50} bins under both equal-width and equal-frequency binning, 12 datasets × 3 rankers × {logistic, rf} × 3 depths | done(e47ab83) — **bin-count-robust**: the random-forest penalty is positive at every bin count under both schemes; exactly one of 72 cells changes sign (uncalibrated logistic, equal-width) and it is material at **none** of the six bin counts, magnitude ≤0.002. Disclosed rather than resolved by choosing a binning. Gradient boosting was not included and the text says so |

## Second enrichment round (author-directed, 2026-08-13..15) — computed on a second machine

> **Numbering note.** `E1`–`E9` above are the *first*-round enrichments and their ids are fixed. The
> proposal notes from that run used a separate `E1`–`E5` / `P1`–`P6` scheme for the same period;
> those are **not** these ids. Everything below is renumbered from `E10` so no id means two things.
> Every entry was verified by `sha256` manifest on the author's box before any number entered the
> manuscript (`AUD-12`), and every number was independently recomputed here from the raw CSVs rather
> than read off the delivered summary.

| id | addition | status |
|---|---|---|
| E10 | **High-dimensional exploratory arm** — four biomedical datasets at $p=279$–$22{,}283$ on an absolute-$k$ grid, plus a controlled $n$-subsampling arm holding $p$ fixed. Answers whether the account extends to the regime where reduction is most often applied | done(d636807) — **negative for the obvious hypothesis**: harm is *not* monotone in $p$ ($-0.278$, $-0.043$, $-0.298$, $-0.159$ at $k=1$), and is not explained by $n/p$ (prostate and arcene share $n/p\approx0.02$ with opposite behaviour; subsampling arrhythmia to $n/p\approx0.36$ leaves the penalty unchanged). Reported as exploratory; the paper's guidance is not extended to this regime |
| E11 | **Cross-dataset correlates of the harm** — is cohort size the hidden variable? | done(d636807) — **cohort size dismissed**: raw $\rho(n,\text{harm})=+0.05$/$+0.22$, and *negative* once $p$ is partialled out ($-0.26$/$-0.20$), while $\rho(p\mid n)=-0.71$ and $\rho(\text{retained-}k)=-0.78$. Every value recomputed here with tie-averaged ranks |
| E12 | **Scalar signal-concentration index** (Gini + top-$k$ share, 16 datasets) — proposed as the property that orders the high-dimensional harm | done(9fe07e7) — 🔴 **refuted, and the refutation is in the paper.** An earlier draft claimed the four datasets are ordered by concentration; tested across three rankers × three statistics it held **2 of 9**, and **0 of 21** once corrected for width (top-$k$ share $\div\,k/p$). Gini ranks arcene above arrhythmia under every ranker while arcene is the more harmed. The claim is withdrawn; only the prostate-vs-arcene contrast (robust 9/9) is retained |
| E13 | **Ensemble disagreement as a probability-independent confidence** — the obvious model-based candidate | done(1ab9e06) — **fails for a structural reason, and we say so**: pooled $\rho$ with $\lvert p-0.5\rvert$ is $-0.991$ over 11,180 out-of-fold points, $\geq0.96$ in magnitude on every dataset. Tree spread is a monotone re-expression of distance from the decision boundary. Not pursued further |
| E14 | **Distance-to-training-support as a genuinely probability-independent confidence** (12 datasets, 106,943 out-of-fold points), with a dedicated check of whether that independence decays with $n$ | done(d636807) — **the most consequential addition of the round.** Limitations previously conceded that establishing selective reliability as independent evidence "would require a confidence estimated outside the predicted probability altogether — which we did not run." It has now been run. The AURC penalty falls $+0.0334\to+0.0116$: **two-thirds of the measured selective-reliability harm is a property of the probability scale**, reported at full prominence in the Discussion and the Abstract, not buried. The surviving third holds at $p=7\times10^{-103}$ with no $n$-dependence ($\rho(n,\text{penalty})=+0.056$, $p=0.86$), and the pooled independence figure is reported as the **unweighted per-dataset mean 0.27** rather than the readmission-dominated pooled 0.40 |
| E15 | **Third and fourth recalibrator** — temperature scaling (1 parameter) and beta calibration (3 parameters), same leakage-safe inner-CV protocol | done(d636807) — ECE $0.0694\to0.0640$ ($-8\,\%$) and $\to0.0504$ ($-28\,\%$); AURC $-3\,\%$ and $+0.6\,\%$; net benefit $0\,\%$ and $+0.8\,\%$. Beta is the decisive case: a flexible *parametric* recalibrator that cuts calibration error by more than a quarter and leaves selective reliability where it found it |
| E16 | **Recalibrator flexibility ladder** — all five recalibrators ordered by free parameters, one matched grid | done(c2f63e8) — ECE recovery is **strictly monotone** in flexibility (Spearman $+1.00$, reaching $27.8\,\%$ of baseline) while AURC recovery is flat-to-negative ($\rho=-0.90$, $\leq3.1\,\%$). Settles the "you did not try a flexible enough recalibrator" objection. **Corrected before publication**: the first version mixed a 36-cell single-ranker baseline with 108-cell all-ranker rungs and carried three different `calib_sha256` values into one table; rebuilt on a matched 108-cell grid where the uncalibrated baselines agree to `0.00e+00`. Net-benefit recovery is reported as *small* ($0.9\,\%$ of baseline), **not** as flat — it is monotone |
| E17 | **Gradient-boosting dedicated sweep** (12 datasets × 3 rankers) — the learner whose raw calibration is not poor | done(e47ab83) — reduction *materially improves* its calibration error while its selective-reliability penalty is simultaneously $+0.028$. The dissociation without the confound of a learner that was badly calibrated to begin with |
| E18 | **Probe-injection dose-response** — a pre-registered, within-dataset *causal* test of the concentration mechanism: inject Gaussian noise features drawn independently of the outcome at $\{1,2,5,10\}\times$ the original width, holding rows, true features, folds and the **absolute** budget fixed | done(99bf6ba) — 🔴 **the pre-registered prediction was refuted and the refutation is reported.** Dilution did not raise the harm; it lowered it (cleveland $+0.054\to+0.006$), reversed it (spectf $+0.004\to-0.037$), or left it unmoved (mammographic $+0.086\to+0.081$). **Reduction defends against noise padding.** The corrected mechanism is sharper than the pre-registered one and explains E12's null: the operative quantity is *how many features carry signal* — an effective dimensionality — which no scalar index expresses across widths differing by two orders of magnitude |

| E19 | **Cross-axis coherence matrix** — the reduction penalty correlated across all five reliability axes over the 108 cells, turning the paper's scattered "the axes disagree" observations into one object | done(c12f765) — the axes split into **two coherent groups**: those defined on the probability *ordering* move together (AURC vs conformal set size $+0.89$), those defined on the probability *scale* move together (ECE vs selective-ECE $+0.97$), and the groups are nearly independent (ECE vs AURC $+0.30$). This is the same division the recalibration ladder implies mechanically, reached from a different direction. **Corrected before use:** as delivered, one axis was not harm-oriented, so its four correlations carried the wrong sign; recomputed here from the released summary with every axis oriented positive-is-worse, all ten magnitudes reproduce and the four conformal signs flip |
| E20 | **Matched absolute budget** — the retained count and $p$ are collinear because the fractional rule sets $k=\lceil0.25pfloor$; hold $k=8$ fixed and ask whether harm still varies with width | done(c12f765) — it does ($ho=esult{+0.77}$, $p=0.016$), so the retained-count association reported in the meta-analysis is **partly that collinearity**, and what a fixed budget discards matters independently of what it keeps. Reported with its restriction: the three narrowest datasets drop out because $k=8$ is not a reduction for them, which removes the cases that would anchor the low end. The pooled figure across both arms is deliberately not used — that section never pools them |
| E21 | **Localisation of the surviving penalty** — is the harm that outlives a probability-independent confidence (E14) the same phenomenon as the distributed-signal account of the high-dimensional arm? | done(c12f765) — **null on all three predictors** (concentration $+0.21$, retained count $-0.16$, $p$ $-0.13$). Two separate findings rather than one mechanism seen twice; low-powered at twelve datasets and labelled as such |
| E22 | **Pre-registered safe-budget diagnostic** — a deliberate attempt to refute the paper's own negative claim, using the ranker's concentration curve as a proxy. Saturation threshold and spike threshold locked in a deposited pre-registration before computing | done(f80b802) — **fails, and the negative claim stands.** Over 80 dataset-by-budget cells: 59\% agreement, sensitivity $1.00$ (no false negatives), specificity $0.15$ (33 safe budgets flagged unsafe). A screen that says unsafe almost everywhere is not a certificate. Had the thresholds been chosen after seeing the cells, a specificity of $0.15$ would have been tuned away and the result reported as a discovery |
| E23 | **Kept-set composition at a fixed budget** | 🔴 **not in the manuscript.** The first version confounded composition with the absolute retained count; the re-run fixed that, and exposed that the kept set itself was selected using the labels outside the cross-validation, biasing the result in the direction measured. Retracted and re-running leakage-free. **The audit that found it also prompted a full read of all 21 enrichment scripts: this is the only affected result** |
### Corrections made during the pre-submission audit, disclosed rather than silently fixed

| what | why it matters |
|---|---|
| The high-dimensional **ordering claim** (E12) was withdrawn | It ordered four datasets on a statistic measured for three, and failed 7 of 9 tests once all four were measured. The uncited `gini` column in our own results refuted it |
| The Discussion's **"harm is predictable … guided by the screen above"** was replaced | Stale text from the submitted version. Results state that *no* proxy certifies a budget in advance — the sentence pointed readers at a criterion the same paper retracts two sections earlier |
| Net-benefit recovery re-described from **"flat"** to **"small"** | It is strictly monotone in recalibrator flexibility. A reviewer ranking five rows sees the rise immediately |
| Method foundations cited **where the method is defined** | ECE, the Brier score, AURC and Platt/isotonic were defined in Methods with their sources cited only in the Introduction |
| `refs.bib` resynchronised with the manuscript | The bibliography is inline, so `refs.bib` is not the build input and had silently lost the Diabetes-130 dataset citation the manuscript cites twice |


## Reviewer 2 (line edits; PDF line refs)

| id | loc | suggestion | disposition | status |
|---|---|---|---|---|
| R2.1 | Abstract l.6 | "At a quarter" → "In a quarter" | accept | done(fb5c064) |
| R2.2 | §1 l.13 | "after features are dropped" → "after features assessed to be redundant are dropped" | accept (with wording) | done(fb5c064) |
| R2.3 | §1 l.15 | "would infer from that evidence" → "might conclude" | accept | done(fb5c064) |
| R2.4 | §1 l.17 | "In the prevailing practice, feature reduction is certified solely on discrimination" | accept | done(fb5c064) |
| R2.5 | §1 l.26 | "at a reduced feature count" → "on the selected set of features"; "auditing what its aggressive application costs" → "assessing the loss due to its aggressive application" | accept | done(fb5c064) |
| R2.6 | §1 l.42 | drop "framework of traditional and novel measures" → "a set of measures that span" | accept | done(fb5c064) |
| R2.7 | §1 l.44 | "it moves" → "it is altered" | accept | done(fb5c064) |
| R2.8 | §1 l.45 | "once for a fixed model" → "only for the final model" | accept (variant) | done(fb5c064) |
| R2.9 | §1 l.46 | "abstain on inputs" → "discard inputs" | decline-with-reason: "abstain" is the standard selective-prediction term; a defining clause added at first use instead | done(fb5c064) |
| R2.10 | §1 l.49 | "—that neither …" → "neither … nor … captures that" | accept | done(fb5c064) |
| R2.11 | §1 l.52 | "we instead ask" → "instead, we ask" | accept | done(fb5c064) |
| R2.12 | §1 l.54 | "are not usually combined" → "are usually not combined"; "justified on" → "justified by" | accept | done(fb5c064) |
| R2.13 | §1 l.56 | "all four" → "all four attributes" | accept | done(fb5c064) |
| R2.14 | §3 l.59 | "instantiates" → "applies" | accept | done(fb5c064) |
| R2.15 | §3 l.83 | "wide-feature" non-standard | accept: defined compact/wide once, formally, at first use (also answers R2.29) | done(fb5c064) |
| R2.16 | §3 l.87 | "extend the same" → "apply the same" | accept | done(fb5c064) |
| R2.17 | §3 l.91 | "For each combination of dataset, …, we run" | accept | done(fb5c064) |
| R2.18 | §3 l.91/93 | $k$ denotes different constants | accept: CV folds renamed (5-fold spelled out); $k$ reserved exclusively for retained features — now load-bearing given R1.1 | done(fb5c064) |
| R2.19 | §3 l.100 | "Per cell we compute, … all from" → "For each cell we evaluate the following quantities, all of them from …" | accept | done(fb5c064) |
| R2.20 | §3 l.109 | parenthetical unclear (class vs group) | accept: rewritten to name outcome classes vs protected subgroups explicitly | done(fb5c064) |
| R2.21 | §3 l.111 | "difference of each outcome" → "difference of the means for each outcome"; "family" → "combination" | accept first; second PARTIAL: "family" is the Holm-correction term of art — kept where it means the multiplicity family and now defined; "combination" used elsewhere | done(fb5c064) |
| R2.22 | §3 l.126 | "were frozen" → "were set (before the data were inspected)" | accept | done(fb5c064) |
| R2.23 | §3 l.127 | "no number …" → "a number is reported only when it regenerates" | accept | done(fb5c064) |
| R2.24 | §3 l.129 | "CSV" → "CSV file" | accept | done(fb5c064) |
| R2.25 | §4 l.140 | monotone claim vs non-monotone left panel of Fig 2 | accept: claim scoped to the MEAN penalty and to AURC/AUROC/NB; text now names which panel; per-dataset ECE non-monotonicity acknowledged | done(fb5c064) |
| R2.26 | §4 Table 3 | redundant — one sentence suffices | accept: table dropped, content folded into §4.2 prose (frees a float for the new decision-curve figure) | done(fb5c064) |
| R2.27 | §4 l.176 | "a wash on average" unclear | accept: plain restatement ("mean change ≈ 0 with material moves in both directions") | done(fb5c064) |
| R2.28 | §4 l.178 | "fairness axes agree" unclear (read as "ages") | accept: sentence rewritten plainly; the misread itself is evidence the phrasing failed | done(fb5c064) |
| R2.29 | §5 l.231 + l.250 | jargon pile-up; define compact/wide, mark in Fig 3 | accept: plain-English restatement; compact/wide defined at first use (p<=12 vs p>=16); Fig-3 marking lands with the regenerated figure | done(fb5c064); fig pending Stage 5 |
| R2.30 | §5 l.265 | "Relation to prior work" → "Relation to established practice" | accept | done(fb5c064) |
| R2.31 | §5 l.276 | "co-move" → "move in tandem" | accept | done(fb5c064) |
| R2.32 | §5 l.284 | "shuffling the labels" → "permuting the labels" | accept | done(fb5c064) |
