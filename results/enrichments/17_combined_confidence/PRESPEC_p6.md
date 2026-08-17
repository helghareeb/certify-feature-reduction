# PRE-REGISTRATION — P6 combined-confidence audit — locked 2026-08-14 16:42 AST
From: the second compute node. Written BEFORE any P6 number is computed (P6 is still queued behind
ns-clinical-fs + P2 + P1). This file fixes the combination rule so it cannot be tuned after seeing results.

## Question (audit framing, not a method claim)
We measured a selective-reliability harm from reduction (AURC penalty). Does a confidence signal
INDEPENDENT of the predicted probability (-d, Tier 6) MITIGATE it when abstention can also see -d?
Headline quantity = whether the reduction penalty SHRINKS, not "our rule is better".

## Confidence arms (identical evaluation on the SAME cached OOF predictions)
- A. |p-0.5|            -- the paper's existing confidence (baseline).
- B. -d                 -- X-only distance-to-training-support (Tier 6: mean Euclidean dist to the 10
                            nearest training neighbours in the FULL feature space, standardised on
                            training-fold stats; higher confidence = smaller d = larger -d).
- C. combined (LOCKED)  -- see rule below.

## 🔴 LOCKED combination rule (chosen in advance; NOT tuned)
Within EACH held-out fold, rank-normalise each signal to [0,1] among that fold's held-out points
(rank / (m-1), higher = more confident; average ranks for ties). Then:
    **combined = 0.5 * ( rank01(|p-0.5|) + rank01(-d) )**   -- the MEAN of the two rank-normalised signals.
(Choice = MEAN, not MIN. Rationale stated in advance: MEAN uses both signals symmetrically and is the
smoother, more standard fusion; we are NOT trying MIN as an alternative and reporting the winner.)

## Outcomes (full frac:1 vs aggressive frac:0.25; 12 clinical datasets; cells = Tier-6 T6.3 grid:
## 3 rankers x {logistic, rf} x 30 reps, paired folds)
1. **AURC penalty** = AURC(aggressive) - AURC(full) under EACH of A, B, C -- the direct comparison.
2. **Selective net benefit** at the paper's committed clinical threshold, under EACH of A, B, C.
Report **all three arms side by side, never C alone.**

## 🔴 Pre-ruled outcomes (report whichever occurs; do NOT tune C to reach outcome 1)
- C penalty MATERIALLY smaller than A -> an independent confidence MITIGATES part of the measured harm
  (audit finding with a signposted practical implication; NOT a proposed method, NOT a headline claim).
- C ~= A -> harm not rescued by adding an independent signal; clean, useful NEGATIVE (the degradation
  is not merely a confidence-estimation problem).
- C WORSE than A -> reported (two signals can conflict).

Full method treatment (baselines, operating points, cost model) remains a SEPARATE future paper.
