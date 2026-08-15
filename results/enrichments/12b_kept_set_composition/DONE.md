# DONE — P1 Arm B (arcene composition, FIXED k=25) + dispersion
2026-08-15 23:58 AST. Confound fixed (budget held at k=25). Penalty RISES monotonically with kept-set
size 0.029->0.091 (CIs disjoint) -> composition matters INDEPENDENT of budget. Mechanism: reduced-25
AUROC falls 0.905->0.821 (top-25 captures less of a more-distributed signal) -> arcene signal DISTRIBUTED
across many features. 180 units/cell, bootstrap 95% CI. Provenance = compute_p1_v2.py + PRESPEC_p1.md.
