# DONE — P1 FINAL (Arm A + leakage-free Arm B v3) — 2026-08-16 15:45 AST
Arm B v3 finished 15:41 (~15.7h; L1-logistic on arcene's 10k features is the long tail). ANCHOR PASSES:
keep=10000 penalty +0.0869 ≈ v2 +0.0914 (Δ0.0045 seed noise) → harness sound. Leakage-free conclusion HOLDS
and is cleaner: at fixed k=25, penalty rises monotonically (+0.027→+0.087, CIs disjoint) and reduced-25
AUROC falls (0.869→0.824) as the kept set widens ⇒ arcene's harm = distributed signal (large effective
dimensionality), NOT irrelevant-feature padding (Arm A). Retraction + fix reported in full. R6 separate.
