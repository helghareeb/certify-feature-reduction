# RESULTS — P1 Arm A (probe injection), with dispersion — shipped ahead of Arm B

**Run:** second compute node · **2026-08-15 ~20:25 AST** · P1 v2 Arm A only (per the Arm A request — Arm B
still running on the arcene tail, unaffected). Pre-registered in `PRESPEC_p1.md`. Now carries
per-(rep,ranker,learner) rows + a seeded 5000/2000-resample bootstrap 95% CI per cell, so each move is a
measured effect, not a direction.

## Design (Arm A)
Inject Gaussian N(0,1) noise features (seed 20260626, independent of y) at doses {0,1,2,5,10}×p, holding
n and the true features fixed; **aggressive budget = fixed absolute k across all doses** (cleveland k=3,
mammographic k=1, spectf k=11). AUROC reduction penalty = AUROC(full) − AUROC(reduced-to-k). 30 reps ×
3 rankers × {logistic,rf} = 180 units/cell.

## AUROC reduction penalty vs dose (mean [bootstrap 95% CI])
| dataset (k) | 0× | 1× | 2× | 5× | 10× | verdict |
|---|--:|--:|--:|--:|--:|---|
| cleveland (k=3) | +0.054 [.050,.058] | +0.043 [.040,.047] | +0.044 [.041,.048] | +0.023 [.017,.030] | **+0.006 [−.002,+.014]** | **material decline** — 0× and 10× CIs disjoint; at 10× the penalty is no longer significantly positive |
| mammographic (k=1) | +0.086 [.082,.091] | +0.084 [.083,.085] | +0.086 [.085,.087] | +0.084 [.083,.086] | +0.081 [.079,.083] | **flat / robust** — stays materially positive at every dose |
| spectf (k=11) | +0.004 [.001,.007] | −0.016 [−.022,−.010] | −0.035 [−.042,−.027] | −0.029 [−.037,−.021] | **−0.037 [−.042,−.032]** | **material flip to beneficial** — CI excludes 0 from 1× on |

## Reading (CI-supported)
Injecting noise does **not** raise reduction harm — the effect is measured, not merely described:
- **cleveland:** harm shrinks materially as noise grows (the reduced top-k model is unaffected; the full
  model degrades on noise, closing the gap).
- **spectf:** reduction flips to materially *beneficial* — cutting removes the injected noise.
- **mammographic:** harm is robust (its single dominant feature is always selected regardless of noise).

So **reduction defends against noise-padding**, and arcene's harm is therefore **not** "too many
irrelevant features" — a padded feature space is filtered by the ranker. (Arm B, shipping next, tests the
composition direction at fixed k; combined they give the distributed-signal mechanism.)

## Deliverables (this Arm-A ship)
`RESULTS_p1_armA.md` · `p1_probe_injection.csv` (per-cell mean + sd + 95% CI + n) ·
`p1_probe_injection_rows.csv` (per-(rep,ranker,learner) rows) · `compute_p1_v2.py` · `PRESPEC_p1.md` ·
`DONE.md` · `MANIFEST.sha256`. Provenance = script + pre-registration (P1 computes fresh; no calib config).
