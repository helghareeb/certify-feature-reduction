# RESULTS — P5: absolute vs fractional k (decoupling retained-count from p)

**Run:** second compute node · **2026-08-16 00:08 AST** · approved enrichment P5, cache-only (main
summary absolute-k arm + high-dim summaries). Tier 8 found "retained-k strongest," but k=0.25·p made
retained-count collinear with p. P5 fixes the ABSOLUTE budget (k=8) and asks: does keeping 8 features
hurt equally regardless of p?

## Harm (AUROC drop) at FIXED k=8, across datasets of differing p
Ordered by p (mean over rankers × learners):
| dataset | p | harm@k=8 |
|---|--:|--:|
| bcw/ilpd/heartfailure | 9–11 | ~0.000 |
| cleveland/statlogheart | 12 | +0.005/+0.008 |
| diabetes130 | 16 | +0.010 |
| hepatitis | 18 | +0.020 |
| spectf | 44 | +0.012 |
| arrhythmia | 279 | +0.083 |
| **prostate_ge** | 5,966 | **−0.007 (helps)** |
| **arcene** | 10,000 | **+0.157** |
| gli85 | 22,283 | +0.034 |

- **Spearman(p, harm@k=8) = +0.598, p=0.031** (13 datasets); **+0.765, p=0.016** (9 clinical only).

## Reading -- retained COUNT alone is not the driver
At a FIXED retained count of 8, harm **rises with p** -- so the Tier-8 "retained-k" association was
partly the k=0.25·p collinearity; the *fraction discarded* (which grows with p at fixed k) matters
independently of the count. **But it is not pure p either:** prostate_ge (p=5,966) is unharmed at k=8
while arcene (p=10,000) is severely harmed -- the distributed-signal distinction from P1/Tier 9. Net: harm
depends on the interplay of retained count, fraction discarded, AND how distributed the signal is -- no
single one of them suffices. Honest refinement of the Tier-8 claim, which should be stated as
"retained-k is *a* strong correlate, partly collinear with width," not "the" driver.

## Deliverables
`RESULTS_p5.md` · `p5_harm_at_absolute_k8.csv` · `p5_summary.json` · `DONE.md` · `MANIFEST.sha256`.
