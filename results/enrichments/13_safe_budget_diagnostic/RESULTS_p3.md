# RESULTS — P3: concentration-curve safe-budget diagnostic (pre-registered; honest negative)

**Run:** second compute node · **2026-08-16 00:15 AST** · approved enrichment P3. Thresholds were LOCKED
in PRESPEC_p3.md BEFORE this computation (saturation k* = smallest k with rf_importance top-k share >=0.90;
"spike" = AURC penalty >= +0.02 absolute; predict UNSAFE iff budget b < k*). Cache-only. Nothing tuned.

## Result vs the pre-set thresholds (80 dataset x budget cells)
- **Agreement = 0.588** · **sensitivity = 1.000** · **specificity = 0.154** · TP=41 FP=33 TN=6 FN=0.

The diagnostic is an **over-conservative, one-sided screen**: it flags every budget that truly spikes
(0 false negatives) but also flags many that do not (33 false positives). k* per dataset ranged 4
(mammographic/haberman) to p (prostate_ge/arcene/gli85, whose curves never reach 90% within the grid --
the distributed-signal datasets from P1).

## Reading (pre-ruled: agreement not high -> report failure, keep the current conclusion)
On the pre-registered thresholds the concentration curve does **NOT** work as a general two-sided
safe-budget proxy -- 59% agreement with 15% specificity is not a usable predictor. **The paper's
"no measured proxy predicts reduction safety" conclusion stands.** 
Honest descriptive nuance (NOT a claim -- the sample is tiny): every cell the curve labelled "safe"
(b >= k*) did turn out safe (NPV 6/6), so the curve behaves as a conservative floor rather than a
predictor; but 6 safe-cells is far too few to rest anything on, so this is noted, not asserted. This is
exactly the outcome pre-registration exists to enforce (cf. Reviewer 1's rho=-0.73): a rule fitted to our
own datasets and reported as a discovery is the error we avoided here.

## Deliverables
`RESULTS_p3.md` · `PRESPEC_p3.md` (the locked thresholds, timestamped before compute) ·
`p3_diagnostic_cells.csv` · `p3_summary.json` · `DONE.md` · `MANIFEST.sha256`.
