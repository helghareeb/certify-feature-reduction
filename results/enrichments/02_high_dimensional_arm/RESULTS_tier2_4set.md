# RESULTS — Tier 2 (COMPLETE, 4-set): high-dimensional boundary arm

**Run:** second compute node · **2026-08-15 ~04:20 AST** · supersedes `RESULTS_tier2_partial`. All four
high-dimensional datasets landed (arcene 8h16m, gli85 ~26h). Same protocol as the partial: k-grid
{1,2,4,8,16,32,64,128,256}, 3 rankers × 3 learners, 30 reps, validated.

## The four points, with the clinical p=44 sets as the low-p anchor
AUROC Δ vs full (negative = worse), mean over 3 rankers × 3 learners:

| dataset | n | p | n/p | k=1 | k=8 | k=64 | k=256 | AURC penalty (k-mean) | material worse/better |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `arrhythmia` | 452 | 279 | 1.62 | −0.278 | −0.083 | −0.006 | +0.001 | +0.083 | 54 / 11 |
| `prostate_ge` | 102 | 5,966 | 0.017 | −0.043 | **+0.007** | **+0.007** | +0.005 | **+0.000** | 22 / 34 |
| `arcene` | 200 | 10,000 | 0.020 | −0.298 | −0.157 | −0.040 | −0.012 | +0.117 | 69 / 8 |
| `gli85` | 85 | 22,283 | 0.0038 | −0.159 | −0.034 | +0.002 | +0.003 | +0.034 | 44 / 6 |

## Headline — the boundary is NOT a p-trend
Ordered by **p** (279 → 5,966 → 10,000 → 22,283), reduction harm goes **hurts → safe → hurts →
moderate** — non-monotone. Higher dimensionality does **not** predict safer reduction. The initial
partial's three-point reading ("harm decreases with p") is corrected here: the fourth and fifth points
(arcene, gli85) break the monotonicity, and we flag it rather than let a referee find it.

It is also **not an n/p-trend**: prostate_ge (n/p=0.017, safe) and arcene (n/p=0.020, most harmful) have
near-identical n/p and opposite behaviour (confirmed within-dataset by Tier 7).

## What DOES order the four — signal concentration (Tier 9)
Rank the four by harm: **prostate_ge < gli85 < arrhythmia < arcene** (least → most harmful). This is the
concentration ordering measured in Tier 9: prostate_ge concentrates its predictive signal in a few
features (selecting preserves it); arcene's signal is diffuse across many features + injected noise
probes (selecting discards it); gli85 is intermediate (harm at k=1 but recovers by k≈32, i.e. moderately
concentrated). **The high-dimensional arm is governed by how concentrated the predictive signal is, not
by p or n/p** — the mechanism is measured in Tier 9 (the prostate_ge/arcene pair) and tested within a
dataset in Tier 7.

## Selective reliability (AURC) tracks the same axis
AURC reduction penalty is **positive** (reduction degrades selective reliability) for every set except
prostate_ge, where it is ~0 — the ECE/AUROC-vs-AURC dissociation and the concentration ordering coincide.

## Framing for the manuscript (the honest, defensible claim)
Not "reduction is safe at high p" (false — arcene). Instead: **"in the p≫n regime, feature reduction can
be neutral/beneficial or strongly harmful depending on how concentrated the predictive signal is; p and
n/p do not determine it, and the concentration of the ranker's scores does."** Consistent with Tiers 7,
8, 9.

## Deliverables
`RESULTS_tier2_4set.md` · `tier2_4set_harm_by_k_auroc.csv` · full per-cell `summary_{arrhythmia,
prostate_ge,arcene,gli85}.csv` · `DONE.md` · `MANIFEST.sha256`. Supersedes the partial (kept as record).
Separate artifact (R6). arcene/gli85 also fold into the Tier-8 and Tier-9 high-dim blocks (updated separately).
