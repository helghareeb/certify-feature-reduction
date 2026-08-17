# RESULTS — Tier 4: ensemble-disagreement confidence for AURC — **sanity STOP (honest negative)**

**Run:** second compute node · **2026-08-13 ~18:10 AST** · per `the Tier 3-5 addendum` + `the Tier 4 plan`.
The cheap safeguard ran first and it is decisive — so no grid was spent.

## What was tested
A confidence signal **not a function of the predicted probability**: the random forest's **per-tree
disagreement** — the standard deviation across the 150 base-forest trees' `predict_proba` on each
held-out fold, computed **before any calibration wrapper**. RF only (logistic is not an ensemble; gb's
trees are additive, not independent). Out-of-fold, main **12-dataset** grid, `mutual_info`, rep 0, full
budget, paired to Tier-1's CV via `derive_seed(20260626, {ds, method, 'rf', rep})` (mean-of-trees == `rf.predict_proba`).

## 🔴 Sanity check (the whole point) — the confidence is NOT independent
**Pooled Spearman( per-tree disagreement std , |p−0.5| ) = −0.9909** over **11,180** out-of-fold points.
Per-dataset (all strongly monotone):

| dataset | ρ | dataset | ρ | dataset | ρ |
|---|--:|---|--:|---|--:|
| cleveland | −0.9999 | statlogheart | −0.9998 | spectf | −0.9998 |
| pima | −0.9999 | haberman | −0.9910 | diabetes130 | −0.9997 |
| ilpd | −0.9998 | hepatitis | −0.9997 | wdbc | −0.9983 |
| heartfailure | −0.9998 | bcw | −0.9998 | mammographic | −0.9635 |

**The disagreement is almost perfectly (inversely) monotone with |p−0.5|.** For a random forest a
prediction near 0.5 is exactly where the trees split hardest (maximal spread), and a prediction near 0
or 1 is where they agree (minimal spread). So tree disagreement *is* essentially a monotone re-expression
of distance-from-0.5 — it induces the **same** risk–coverage ordering, and therefore the **same** AURC.

## Verdict — as pre-specified 3: **STOP, and the limitation stands**
`|ρ| = 0.991 ≥ 0.95` → this confidence is **not independent** of the predicted probability, so it cannot
test whether selective reliability is independent evidence. Following the pre-ruling exactly: **report the
correlation and stop; the manuscript's concession stands as written** —

> *"AURC uses confidence |p−0.5|, a monotone function of the predicted probability itself; selective
> reliability and calibration are therefore not fully independent and are expected to move in tandem."*

— and this route (RF tree disagreement) does **not** upgrade it to a measurement.

**Note on the alternative measure:** the addendum offered vote-margin across trees as the other option. It
is the margin of the tree *vote fraction*, and the vote fraction ≈ the mean probability, so it is likewise a
monotone function of |p−0.5| and would give the same verdict; std is reported as the cleaner continuous
disagreement. **I have not gone looking for a third confidence to restore the result** (as pre-specified).
A genuinely p-independent signal would have to come from *outside* the probability — e.g. feature-space
distance-to-training-support or a separate uncertainty model — which is a different experiment; flagging it
as an option, not doing it.

**Reported at full prominence as an honest negative**, exactly as the indeterminacy and stability nulls were.

## Deliverables
`tier4_sanity.json` (ρ, n, verdict) · this `RESULTS_tier4.md` · `DONE.md` · `MANIFEST.sha256`. Separate artifact, not merged with any grid (R6). No raw caches.
