# RESULTS — smk_can_187: 5th high-dimensional dataset (enrichment item 3)

**Run:** second compute node · **2026-08-17 ~03:20 AST** · SMK-CAN-187 (n=187, p=19,993; n/p=0.0094;
prevalence 0.52), run under `config/calibration_highdim.json` exactly as the other wide sets (absolute-k grid
k∈{1,2,4,8,16,32,64,128,256}+full, 3 rankers × 3 learners × 30 reps). Sharded 9 ways (ranker×learner) via
run_highdim.py, merged directly (merge_shards' expected-row check assumes the config's datasets, not a
`--datasets` override, so it errored on prostate_ge; the 9 raw shards are complete and merged here). Reported
as a separate artifact, never pooled with the twelve clinical datasets.

## Harm curve — AUROC penalty (full − reduced), paired per unit, mean over 3 rankers × 3 learners × 30 reps
| k | AUROC penalty | sd |
|--:|--:|--:|
| 1 | **+0.176** | 0.050 |
| 2 | +0.137 | 0.048 |
| 4 | +0.093 | 0.045 |
| 8 | +0.053 | 0.044 |
| 16 | +0.029 | 0.043 |
| 32 | +0.016 | 0.043 |
| 64 | +0.008 | 0.042 |
| 128 | +0.004 | 0.036 |
| 256 | −0.002 | 0.027 |

Monotone: severe at k=1 (−0.176 in the paper's sign convention), neutral by k≈256. Full-feature AUROC 0.755.

## How it fits the high-dim narrative (reinforces two existing points; overturns nothing)
**1. Higher dimensionality does NOT predict safer reduction.** Ordered by p:

| dataset | p | AUROC penalty @k=1 |
|---|--:|--:|
| arrhythmia | 279 | −0.278 |
| prostate_ge | 5,966 | −0.043 |
| arcene | 10,000 | −0.298 |
| **smk_can_187** | **19,993** | **−0.176** |
| gli85 | 22,283 | −0.159 |

smk (p=19,993) is **less harmed than arcene** (p=10,000) — the non-monotonic-in-p pattern the paper already
reports, now with a 5th point between arcene and glioma.

**2. A single concentration index does not order the harm (the paper's honest negative), reinforced.** smk
top-8 in-budget share: L1 0.203, RF 0.023, MI 0.002. Under **L1** smk is more concentrated than arcene (0.150)
AND less harmed — consistent with concentration. Under **RF** smk is *less* concentrated than arcene (0.029)
yet still less harmed — inconsistent. So smk is another dataset the scale-free/in-budget statistics rank
differently across rankers, exactly as the paper states for the four-dataset set. **The prostate-vs-arcene
contrast (prostate more concentrated AND less harmed under every ranker) is untouched — smk is a new point,
not a re-test of that pair.**

## Honest note on runtime (root cause + fix)
One-shard bench projected ~2.54 h; the 9-shard run actually took ~5 h. Cause: the gradient-boosting shards'
internal OpenMP threads oversubscribe the box under 9-way concurrency, inflating wall-clock (NOT correctness —
process-level shards, in-estimator n_jobs=1, bit-identical). Fix for next time: `OMP_NUM_THREADS=1` on the gb
shards, beside the existing n_jobs=1 rule. Judged worth finishing (idle machine, completeness-over-speed);
confirmed on review.

## Deliverables (flat zip, scripts inside)
`RESULTS_highdim_smk.md` · `smk_harm_by_budget.csv` · `smk_concentration.csv` (per-ranker Gini + top-k shares)
· `smk_can_187_merged.csv` (2,700 per-cell raw rows) · `run_smk_shards.sh` · `DONE.md` · `MANIFEST.sha256`.
