# RESULTS — Tier 6: distance-to-training-support as a probability-independent confidence

**Run:** second compute node · **2026-08-15 ~10:35 AST** · per `the Tier 6 addendum`. **12/12 datasets**
(diabetes130 at the full 101,763 cohort). Confidence = −d = mean Euclidean distance to the m=10 nearest
neighbours in the FULL feature space, standardised on training-fold stats only, same −d across budgets.

## T6.2 sanity — −d IS independent of the predicted probability (the opposite of Tier 4)
Pooled Spearman(−d, |p−0.5|) = **+0.402** over 106,943 OOF points → verdict **proceed_independent**
(<0.5). Tier 4's per-tree disagreement was ρ=−0.991 (killed); −d is a genuinely independent signal.

🔴 **But the pooled figure is diabetes130-dominated** (its 101k points are 95% of the pool). The
**unweighted mean per-dataset ρ = 0.267** — lower than the pooled 0.402 — and per-dataset ρ spans
**[−0.65 (spectf), +0.74 (hepatitis)]** with mixed signs. This is the "partial independence" predicted:
near-support points are *somewhat* likelier to be confidently predicted, but −d is not a re-expression
of p. diabetes130's own ρ=+0.424 is **not** extreme (hepatitis +0.74 and bcw +0.68 are higher at small
n), so the high pooled value is a point-weighting artifact, not an n-effect on independence.
**Enrichment E2 formalises this** (per-dataset ρ vs n; unweighted mean beside pooled).

## T6.3 measurement — the AURC reduction penalty under −d vs |p−0.5| (12/12, 2,160 cells)
Reduction penalty = AURC(aggressive frac:0.25) − AURC(full frac:1); reuse cached OOF p, no refit.

| confidence | mean penalty |
|---|--:|
| \|p−0.5\| (probability scale) | **+0.03345** |
| **−d (X-only, independent)** | **+0.01163** |
| survival ratio (d / margin) | **0.35** |
| Wilcoxon p (penalty_d ≠ 0) | **7.2×10⁻¹⁰³** |

## Reading (pre-ruled: shrinks materially, but a real surviving component)
- **~65% of the AURC reduction penalty was a property of the probability scale** — it disappears when
  the confidence is computed from X alone. Reported at full prominence as a publishable correction.
- **~35% SURVIVES under a genuinely probability-independent confidence, and that third is
  overwhelmingly significant** (Wilcoxon p=7×10⁻¹⁰³, positive). So selective reliability is **partly
  independent evidence** — not purely a shadow of p. The manuscript's concession is upgraded from "not
  independent" to a measured "a material fraction of the selective-reliability degradation persists
  under a probability-independent confidence; the majority reflects the probability scale."
- **Did NOT hunt for a further confidence to restore the penalty** — reporting exactly what −d gives.

Per-dataset penalty_d mostly positive (cleveland +0.025, mammographic +0.029, statlogheart +0.028, pima
+0.026, hepatitis +0.016); a few ~0 or slightly negative (haberman −0.012, spectf −0.002, ilpd −0.000);
diabetes130 +0.002. The surviving signal is real but modest and dataset-dependent (E4 localises it).

## Deliverables
`RESULTS_tier6.md` · `tier6_sanity.json` (pooled + per-dataset ρ, 12 ds) · `tier6_measurement_12ds.csv`
· `tier6_measurement_12ds_summary.json` · `DONE.md` · `MANIFEST.sha256`. Separate artifact (R6).
🔴 The Tier-6 write-up is GATED on E2 (per-dataset ρ vs n), since the pooled independence figure is
diabetes130-dominated — E2 runs next.
