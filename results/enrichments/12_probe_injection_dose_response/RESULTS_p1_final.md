# RESULTS — P1 FINAL (Arm A + leakage-free Arm B v3) — COMPLETE

**Run:** second compute node · **2026-08-16 ~15:45 AST** · pre-registered in `PRESPEC_p1.md`. This is the
FINAL P1 delivery: Arm A (probe injection, unchanged) + **Arm B v3, the LEAKAGE-FREE re-run** that replaces
the retracted v1/v2 Arm B. The retraction and the fix are reported in full — the corrected result is the
honest and stronger one, and it **confirms** the distributed-signal mechanism.

---
## Retraction + fix (why v3 exists)
The the pre-submission code review found a **label-leakage** in Arm B v1/v2: the kept set was chosen by ranking the
**whole dataset (labels included) ONCE outside CV**, so the reduced-25 model drew from a label-optimised
pool — an optimistic bias. **Fix (v3):** the kept pool is selected **inside each training fold on train
labels only**, then ranked within the pool and reduced to a fixed k=25. Frozen code untouched; the fix lives
only in the enrichment driver `compute_p1b_v3.py`.

**Anchor check (harness soundness):** at keep=10000 the pool is *all* features either way, so leakage
vanishes there and v3 must reproduce v2. It does: **v3 penalty = +0.0869 vs v2 +0.0914** (Δ=0.0045, pure
seed noise — v3 adds a `keep` key to the fold seed). The harness is sound; only the label-biased small-keep
rows could move, and the conclusion below is drawn from the clean run.

---
## Arm A — inject Gaussian noise features (dilute); fixed n, fixed true signal, fixed absolute k
30 reps × 3 rankers × {logistic,rf} = 180 units/cell; bootstrap 95% CI. AUROC reduction penalty vs dose:

| dataset (k) | 0× | 1× | 2× | 5× | 10× | verdict |
|---|--:|--:|--:|--:|--:|---|
| cleveland (k=3) | +0.054 | +0.043 | +0.044 | +0.023 | **+0.006** | material decline (0× vs 10× CIs disjoint) |
| mammographic (k=1) | +0.086 | +0.084 | +0.086 | +0.084 | +0.081 | flat / robust |
| spectf (k=11) | +0.004 | −0.016 | −0.035 | −0.029 | **−0.037** | material flip to beneficial |

**Reduction defends against noise-padding** — injecting irrelevant features does not raise harm; the ranker
filters them (cleveland harm shrinks, spectf flips beneficial, mammographic's dominant feature is always
kept). ⇒ arcene's harm is **NOT** "too many irrelevant features."

---
## Arm B v3 — LEAKAGE-FREE composition test (arcene), fixed budget k=25
Keep arcene's top-k rf-importance features (pool chosen IN-FOLD) for keep ∈ {100,256,1000,5000,10000};
within the pool reduce to a fixed **k=25**. 30 reps × 3 rankers × {logistic,rf} = 180 units/keep; bootstrap
95% CI. Only the *composition* of the available set changes; the budget is constant.

| kept | full-kept AUROC | reduced-25 AUROC | penalty [95% CI] |
|--:|--:|--:|--:|
| 100 | 0.8961 | 0.8688 | +0.0273 [.0237,.0308] |
| 256 | 0.8997 | 0.8676 | +0.0321 [.0296,.0348] |
| 1000 | 0.9085 | 0.8486 | +0.0599 [.0549,.0649] |
| 5000 | 0.9132 | 0.8387 | +0.0745 [.0678,.0817] |
| 10000 | 0.9109 | 0.8240 | +0.0869 [.0785,.0960] |

**At fixed budget, the penalty rises monotonically** (+0.027 → +0.087, CIs disjoint end-to-end) **and the
reduced-25 AUROC falls monotonically** (0.869 → 0.824) as the available set widens, while full-kept stays
high (0.90–0.91). The direction is unchanged from the (leaky) v2 — the leakage fix lowers the magnitudes
slightly but does not alter the shape or the sign. Per the pre-ruling, non-flat-at-fixed-budget ⇒
**composition matters independently of the budget.**

---
## Mechanism (both arms converge, now leakage-free)
A fixed budget of 25 features captures **less and less** of arcene's signal as more of that signal becomes
available to lose — because arcene's predictive signal is **distributed across hundreds of features (large
effective signal dimensionality)**, not concentrated in a handful. Restrict to a pre-concentrated top-100
set and 25 features capture most of it (reduced-25 = 0.869, small penalty); expose the full distributed set
and 25 is far too few (reduced-25 = 0.824, large penalty).

## Combined P1 conclusion (CI-supported, leakage-free)
- **Arm A:** reduction *defends against* injected noise → arcene's harm is NOT "too many irrelevant features."
- **Arm B v3:** at fixed budget, harm grows with how much *real, distributed* signal is available → arcene's
  harm IS that its signal is spread across many features.
- Together: a causal, within-dataset account (same rows, same folds; only the feature set changes) of why
  aggressive reduction harms arcene, and why Tier 9's scalar concentration index was null across widths —
  the operative quantity is *how many features carry the signal*, measured here directly.

## Deliverables (flat zip, code inside per N17)
`RESULTS_p1_final.md` · `p1_probe_injection.csv` + `p1_probe_injection_rows.csv` (Arm A) ·
`p1_arcene_reverse_v3.csv` + `p1_arcene_reverse_v3_rows.csv` (Arm B v3, leakage-free) ·
`compute_p1_v2.py` (Arm A code) · `compute_p1b_v3.py` (Arm B v3 leakage-free code) · `PRESPEC_p1.md` ·
`DONE.md` · `MANIFEST.sha256`. R6 separate artifact; P1 computes fresh (no calib config).
