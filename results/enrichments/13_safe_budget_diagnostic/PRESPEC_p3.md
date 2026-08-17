# PRE-REGISTRATION — P3 concentration-curve safe-budget diagnostic — locked 2026-08-16 00:13 AST
From: the second compute node. Written BEFORE computing any agreement (thresholds fixed so nothing is tuned
to the result), per the agent's non-negotiable condition. Cache-only.

## Hypothesis
Within a dataset, the ranker's top-k cumulative-share CURVE predicts the budget below which reduction
loses signal: if the curve has captured the signal by your budget, reduction is safe; if not, expect an
AURC (selective-reliability) penalty.

## 🔴 LOCKED thresholds (both fixed in advance)
(a) **Saturation k\*** (per dataset) = the smallest k in {1,2,4,8,16,32,64,128,256} at which the
    **rf_importance** mean top-k cumulative share (from tier9_concentration.csv) is **>= 0.90**. If the
    curve never reaches 0.90 within the grid, k\* = p (never saturates).
(b) **"AURC penalty spikes at budget b"** = the mean AURC reduction penalty at retained-k = b
    (delta vs full, meaned over rankers x learners) is **>= +0.02** (absolute), a FIXED threshold.
(c) **Diagnostic prediction:** budget b is UNSAFE iff **b < k\***.

## Test (pre-committed)
Over every (dataset, budget b) cell for which both the share curve and an absolute-k AURC penalty exist
(clinical b in {1,2,4,8}; high-dim b in {1..256}), compare predicted-unsafe (b<k\*) to observed-spike
(penalty>=+0.02). Report **agreement = fraction of cells where they match**, plus sensitivity and
specificity. **No success threshold is cherry-picked after the fact.**

## Pre-ruled outcome
- High agreement -> the concentration curve is a working within-dataset safe-budget proxy (the first the
  paper would have found; every scalar proxy failed). Reported as a practitioner tool.
- Low agreement -> the diagnostic does NOT predict safety on the pre-set thresholds; report the failure
  and keep the paper's current "no proxy predicts safety" conclusion. Descriptive at this many datasets.
