# QUERY (Tier 2) — 🔴 the fracs budget grid DEGENERATES on 3/4 sets → your call on an absolute-k grid

**Run:** second compute node · **2026-08-13 ~13:35 AST** · re: your `the Tier 2 sign-off.md` §4 retention gate.
**Stopping before the full run exactly** — the budget grid is a science decision and it's yours.

## 1. Budget-retention gate — RESULT: degenerate for the high-p sets
`fracs = [1, 0.75, 0.5, 0.33, 0.25]`, retained-k vs n:

| dataset | n | p | retained-k per frac | verdict |
|---|--:|--:|---|---|
| **Arrhythmia (bridge)** | 452 | 279 | 279, 209, 140, 92, 70 | ✅ ok (all k < n) |
| Prostate-GE | 102 | 5,966 | 5966, 4474, 2983, 1969, 1492 | 🔴 **all k ≫ n** |
| Arcene | 200 | 10,000 | 10000, 7500, 5000, 3300, 2500 | 🔴 **all k ≫ n** |
| GLI-85 | 85 | 22,283 | 22283, 16712, 11142, 7353, 5571 | 🔴 **all k ≫ n** |

For 3 of 4 sets **every fractional budget retains more features than there are samples** — none reach the
aggressive single-digit/low-count regime where the low-dim arm shows the harm. Running fracs there would
**not measure the same thing** as the p=3–44 arm; it would just compare large-k to larger-k.

## 2. 🔴 Proposal (your ruling requested): an ABSOLUTE-k grid, matched to the harm regime
The runner already supports `budgets.ks`. Proposed, to reach the same aggressive counts across all p:
`ks = [2, 4, 8, 16, 32, 64, 128, 256, 512]` plus `frac:1.0` as the full-feature reference.
This maps every dataset (bridge included, for consistency) onto the same retained-feature counts, so the
contrast is "same k, different p" — an actual boundary characterisation (44 → 279 → 6k → 22k). **Your call
on the exact k values / whether to keep any fracs.** I have written nothing into a config until you rule.

## 3. Bridge dataset — Arrhythmia CONFIRMED and verified
UCI Arrhythmia (id 5): **n=452, p=279**, cardiac; binarized normal(class 1) vs arrhythmia(2–16) =
**245/207 (45.8% positive — well balanced)**. Non-degenerate under fracs. sha256(raw)=`a7f0f4ca289a4c58b5ed…`,
402,355 bytes, at `_staging/highdim/arrhythmia/`. UCI licence. Excellent fit for the p≈100–1,000 bridge.

## 4. Provenance (your §1 ask) — OpenML check
- **Arcene** is on OpenML (ids **1458**, **41157**) — plus its UCI CC BY 4.0 source. Clean.
- **SMK-CAN-187, GLI-85, Prostate-GE**: **not found on OpenML** under these names. So their source of record
  would be the **original studies (GEO accessions)**, not OpenML. Flagging for your provenance decision —
  if an OpenML-backed source is required, we may prefer datasets that have one.

## 5. Housekeeping
- `RESULTS_tier1.md` **re-shipped** (sha now `77a6a3e1…`, 6× "material" — the correct post-13:02 version).
- diabetes130 calibrated addendum continues (detached, low-priority).

**On your ruling (k-grid + provenance), I write the loader + `config/calibration_highdim.json` and run smallest-p first.**
