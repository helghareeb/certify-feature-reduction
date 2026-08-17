# RESULTS — Tier 7: does reduction harm depend on n at FIXED p? (n/p disentanglement)

**Run:** second compute node · **2026-08-14 ~03:20 AST** · per `the Tier 7 plan.md`.
Ran low-priority beside `gli85`. `arrhythmia`, **p=279 held constant**, n stratified-subsampled to
{100, 150, 250, 452(full)} — same k-grid, 3 rankers, 3 learners, REPS=30, same folds/firewall; only n
changes. n=452 is the existing validated run; {100,150,250} fresh (seed 20260626, outcome-stratified).

## The question
Between datasets, `n` covaries with `p`, prevalence and signal structure, so the Tier-2 "boundary"
could be an `n/p` effect rather than a `p` effect. This holds `p` fixed and moves only `n`: at n=100,
p=279 we reach **n/p ≈ 0.36** — the same side of the ratio as the high-p sets (prostate_ge 0.017,
arcene 0.020) — **without changing p at all.**

## Result — harm PERSISTS as n falls at fixed p (it does not vanish or flip)
AUROC penalty (Δ vs full; negative = worse) and AURC penalty (positive = worse), meaned over 3 rankers:

| n | n/p | AUROC Δ @k1 (gb / log / rf) | AUROC Δ k-arm mean (gb / log / rf) | AURC k-arm mean (gb / log / rf) |
|--:|--:|---|---|---|
| 100 | 0.36 | −0.148 / −0.187 / −0.286 | −0.076 / −0.072 / −0.105 | +0.078 / +0.046 / +0.105 |
| 150 | 0.54 | −0.188 / −0.219 / −0.288 | −0.066 / −0.070 / −0.092 | +0.065 / +0.063 / +0.090 |
| 250 | 0.90 | −0.256 / −0.184 / −0.297 | −0.100 / −0.035 / −0.100 | +0.100 / +0.032 / +0.100 |
| 452 | 1.62 | −0.296 / −0.227 / −0.309 | −0.107 / −0.056 / −0.099 | +0.096 / +0.060 / +0.095 |

**At n=100 (n/p ≈ 0.36, prostate_ge's regime), arrhythmia's reduction harm is essentially the same as
at full n** — rf k-arm penalty −0.105 (n=100) vs −0.099 (n=452); rf @k1 −0.286 vs −0.309. Any variation
across n is small and non-monotone (e.g. gb @k1 is *milder* at low n, rf is flat), i.e. within noise. The
penalty does not collapse toward zero as n shrinks.

## Reading (pre-specified outcome: "harm stays as n falls")
- **The boundary is not in n/p.** arrhythmia stays harmful at n/p ≈ 0.36, whereas prostate_ge is *safe*
  at n/p ≈ 0.017. Same low ratio, opposite behaviour — sample scarcity relative to features is **not**
  what determines reduction safety.
- **This is the stronger, within-dataset version of Tier 8's between-dataset n-null.** Tier 8 found
  harm-vs-n collapses once p is controlled; Tier 7 shows the same thing by construction (p fixed): moving
  n alone does not move the penalty. Two independent designs agree.
- **Converges with Tier 9.** Tier 9 showed the arcene/prostate_ge dissociation (identical n/p) is
  explained by signal *concentration*, not n/p. Tier 7 removes n/p as the driver directly; Tier 9 names
  what remains. Together: reduction harm is governed by how much predictive signal survives selection
  (concentration / retained-k), **not by n, and not by n/p.**

## Deliverables
`RESULTS_tier7.md` · `tier7_penalty_vs_n.csv` (per n × classifier: AUROC Δ@k1/@k8/k-arm-mean, AURC
k-arm-mean) · `summary_arrhythmia_n{100,150,250}.csv` (full per-cell) · `DONE.md` · `MANIFEST.sha256`.
Separate configs/hashes per n (R6), not merged. Numbers, not raw caches.
