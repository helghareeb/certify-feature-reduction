# PRE-REGISTRATION — P1 probe-injection dose-response — locked 2026-08-15 10:48 AST (before any P1 number)
From: the second compute node. Design fixed in advance per the approval.

## Question (audit, causal-within-dataset)
Does DILUTING signal concentration (adding pure-noise features) increase reduction harm, and does
CONCENTRATING it (dropping the weakest features) decrease harm? Same rows, same true features, same folds
-- only the noise columns change -> isolates concentration as the cause.

## Arm A -- probe injection (dilute)
- Datasets: **cleveland, mammographic** (reduction-hurts side) + **spectf** (near-zero harm control).
- Doses (added Gaussian probes as a multiple of original p): **{0x, 1x, 2x, 5x, 10x}**.
- Probes ~ N(0,1) i.i.d., drawn INDEPENDENTLY of y; noise seed = derive_seed(20260626,{'probe',dataset,dose})
  -- FIXED per (dataset,dose), identical across reps (reps vary only the CV folds).
- Full budget = all features at that dose (p_original x (1+dose)); aggressive budget = FIXED absolute
  k = round(0.25 x p_original), the same k at every dose.
- REPS=30, 3 rankers x {logistic, rf}, StratifiedKFold(5), same firewall as the study.
- Report per (dataset,dose): reduced-model AUROC, AUROC penalty (full-reduced), AURC penalty
  (reduced-full), and the measured top-k concentration share -- so harm can be plotted vs measured
  concentration, not just vs dose.

## Arm B -- reverse concentration on arcene (PREFERRED demonstration)
- Keep the top-{100, 256, 1000, 5000, all(10000)} rf-importance features (raising concentration as fewer,
  better features remain), measure the reduction penalty at each -> does harm FALL as concentration rises?

## Pre-ruled
- Harm rises with dilution / falls with concentration -> concentration ESTABLISHED as the causal driver
  (answers the "n=1 pair" objection with a controlled curve).
- Flat / no movement -> concentration is not causal; report it plainly and the matched pair stands alone.
- Non-monotone -> report as measured, do not smooth.
