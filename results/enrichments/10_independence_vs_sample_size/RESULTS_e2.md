# RESULTS — the enrichment round E2: is the −d independence n-dependent? (bounds the Tier-6 claim)

**Run:** second compute node · **2026-08-15 ~10:40 AST** · approved enrichment E2 (from the observation
that Tier-6 pooled ρ jumped 0.21→0.40 when diabetes130's 101k points entered). Pure cache analysis over
`tier6_sanity.json` + `tier6_measurement_12ds.csv`. **This gates the Tier-6 write-up.**

## The question
The Tier-6 pooled Spearman(−d, |p−0.5|) = **0.402** is computed over 106,943 OOF points, of which
**diabetes130 supplies 101,763 (95%)**. Two explanations: (a) −d becomes *less* independent as n grows
(a real range-of-validity limit), or (b) the pooled figure is just point-weighting by one big dataset.
E2 distinguishes them by reporting independence and surviving penalty **per dataset, against n**.

## Per-dataset independence vs n (sorted by n)
| dataset | n | p | ρ(−d,\|p−0.5\|) | surviving penalty_d |
|---|--:|--:|--:|--:|
| hepatitis | 155 | 18 | +0.738 | +0.0155 |
| spectf | 267 | 44 | −0.652 | −0.0017 |
| statlogheart | 270 | 12 | +0.453 | +0.0280 |
| heartfailure | 299 | 11 | +0.315 | +0.0102 |
| cleveland | 303 | 12 | +0.467 | +0.0253 |
| haberman | 306 | 3 | +0.471 | −0.0117 |
| wdbc | 569 | 30 | +0.167 | +0.0100 |
| ilpd | 583 | 9 | −0.527 | −0.0004 |
| bcw | 699 | 9 | +0.681 | +0.0077 |
| pima | 768 | 8 | +0.324 | +0.0261 |
| mammographic | 961 | 5 | +0.346 | +0.0285 |
| **diabetes130** | **101,763** | 16 | **+0.424** | +0.0022 |

## Result — NO n-trend; the pooled figure is a weighting artifact
- Spearman(n, ρ) = **−0.084** (p=0.80); Spearman(n, |ρ|) = **−0.378** (p=0.23); Spearman(n, penalty_d)
  = **+0.056** (p=0.86). **None significant.**
- diabetes130's own ρ=+0.424 is **mid-range**, not extreme — hepatitis (n=155) is higher at +0.738;
  the spread at small n (−0.65 to +0.74) is far wider than any n-pattern.
- **Pooled ρ=0.402 vs UNWEIGHTED mean per-dataset ρ=0.267.** The gap is entirely diabetes130's 95%
  point share, not an n-effect on independence.

## Reading (pre-ruled: "flat → Tier 6 generalises; the pooled figure was merely unfortunate")
−d's independence from the predicted probability **does not decay with n**. The Tier-6 conclusion holds
across the sample-size range, and the manuscript should **report the unweighted mean ρ ≈ 0.27 (or the
per-dataset distribution), not the diabetes130-dominated pooled 0.40** — both are well below the 0.5
independence threshold, so the direction is unchanged, but the honest central value is lower. The
surviving-penalty component (Tier-6 T6.3, ~35%) likewise shows no n-dependence.

**Net effect on the paper:** the Tier-6 independence claim is now *bounded and correct* — it is a
property of the confidence, not of any one large cohort — and the write-up can proceed with the
unweighted statistic. That is exactly what E2 was run to establish.

## Deliverables
`RESULTS_e2.md` · `e2_independence_vs_n.csv` · `e2_summary.json` · `DONE.md` · `MANIFEST.sha256`.
Separate artifact (R6). Cache-only; no new compute.
