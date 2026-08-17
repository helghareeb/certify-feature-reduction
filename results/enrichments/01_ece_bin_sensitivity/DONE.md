# DONE — Tier 1 (updated with Holm materiality)

**Second compute node · 2026-08-13 13:1x AST**

- T1.1 widened OOF cache (216 cells; calibration_tier1.json; separate artifact, NOT merged w/ submitted grid).
- 🔬 T1.2 ECE bin-sweep {5,10,15,20,30,50} × equal-width/equal-freq (full table, no elisions) + Holm materiality:
  * logistic/none sign flip is INSIDE NOISE — not material at ANY bin count (p_holm=1.0 EW; 0.15-0.64 EF); crossover 10->15 bins is equal-width-only.
  * rf/none is material at ALL bins under equal-FREQUENCY but not equal-width => materiality depends on binning scheme, not just bin count.
  * reported per pre-ruling, no bin-count selection; rf not led ahead of the honest logistic story.
- 🔬 T1.3 AURC under |p-0.5| / |2p-1| / entropy: |p-0.5|==|2p-1| exact, entropy <=6.7e-3 => penalty survives, invariant.
- Coverage: none=12; sigmoid/isotonic=11. diabetes130 calibrated = OPTION 2 RUNNING (detached, low-priority) as pre-specified -> the delivery archive later.
- Files: RESULTS_tier1.md, tier1_ece_binsweep.csv, tier1_ece_materiality.csv, tier1_aurc_confidence.csv, calibration_tier1.json, env_freeze.txt, MANIFEST.sha256.
