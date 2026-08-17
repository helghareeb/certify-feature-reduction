# RESULTS — Tier 5: extend the ECE bin-sweep to gradient boosting (closes the gb caveat)

**Run:** second compute node · **2026-08-14 ~15:40 AST** · per `the Tier 3-5 addendum` T5.1.
gb was generated with `config/calibration_tier5.json` — **byte-identical to `calibration_tier1.json`
except {classifiers:[gb], calibrations:[none,sigmoid,isotonic], p_oof_cells: the 108 gb cells}** — on the
**frozen, Stage-0 reproduction-gated runner, unchanged**. So gb's OOF probabilities are exactly what
Tier 1 would have cached for gb; parallel execution does not touch the numbers. **12/12 datasets, 3
rankers, 3 recalibration depths, 30 reps** (3,240 cells). T1.2 protocol repeated exactly.

## T5.1 — ECE reduction penalty (full frac:1 vs aggressive frac:0.25), bins {5,10,15,20,30,50}, EW+EF
Penalty = ECE(reduced) − ECE(full); negative = reduction *improves* ECE. Mean over 12ds × 3 rankers × 30 reps:

| calibrate | b5 | b10 | b15 | b20 | b30 | b50 | direction |
|---|--:|--:|--:|--:|--:|--:|---|
| **none** | −0.0216 | −0.0189 | −0.0175 | −0.0170 | −0.0158 | −0.0136 | **stable −** |
| **sigmoid** | −0.0064 | −0.0040 | −0.0031 | −0.0030 | −0.0028 | −0.0031 | stable − |
| **isotonic** | +0.0043 | +0.0011 | +0.0003 | −0.0009 | −0.0027 | −0.0053 | **flips (15→20)** |

## T5.1 materiality — Holm-corrected across the 6 bin counts (unit = dataset×method)
| calibrate | bin_type | materiality |
|---|---|---|
| **none** | equal-width | **material − at every bin (b5–b50)** |
| **none** | equal-freq | material − at b5,b10,b15,b20 |
| sigmoid | both | not material |
| **isotonic** | equal-width | **flip NOT material at any bin** (p_holm 0.10→1.0; crossover 15→20) |
| **isotonic** | equal-freq | **flip NOT material at any bin** (crossover 20→30) |

**Reading:** for **uncalibrated gb, aggressive reduction materially *improves* ECE** — a real, stable,
Holm-surviving effect. The only sign change (gb+isotonic) is **inside noise** — it never reaches
materiality at any bin count, exactly as the Tier-1 logistic/none flip did. **No bin count was selected
to preserve a conclusion**, and the manuscript's conclusions are robust to including gb.

## T5.1 — AURC reduction penalty (gb exhibits the same dissociation)
| calibrate | AURC penalty | margin \|p−0.5\| | entropy | \|2p−1\| |
|---|--:|--:|--:|--:|
| none | +0.0284 | +0.028369 | +0.028369 | +0.028369 |
| sigmoid | +0.0304 | +0.030375 | +0.030375 | +0.030375 |
| isotonic | +0.0287 | +0.028750 | +0.028931 | +0.028750 |

The AURC penalty is **positive** for gb (reduction degrades selective reliability) while ECE *improves* —
the **same ECE-recovers / AURC-degrades dissociation** the manuscript reports for logistic and rf. The
three confidence measures are identical for none/sigmoid; isotonic shows a 1.8×10⁻⁴ spread (isotonic's
step-function ties, not a real difference).

## Bottom line
gb does **not** behave unlike logistic and rf: aggressive reduction improves calibration (ECE) but
degrades selective reliability (AURC), and the effect is bin-robust (only an immaterial isotonic wobble).
The §Limitations sentence "Gradient boosting was not included in this control" can be removed — it is now
included, and it confirms rather than complicates the finding.

## Deliverables
`RESULTS_tier5.md` · `tier5_ece_binsweep.csv` · `tier5_ece_materiality.csv` · `tier5_aurc_confidence.csv`
· `DONE.md` · `MANIFEST.sha256`. Separate artifact, not merged (R6). Numbers, not caches.
