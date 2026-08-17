# STATUS — Tier 2 boundary arm LAUNCHED (pre-run retained-k gate + provenance)

**Run:** second compute node · **2026-08-13 ~13:50 AST** · acting on `the Tier 2 budget grid.md`.

## Retained-k from the ACTUAL config (your pre-run gate — non-degenerate as built ✅)
`ks=[1,2,4,8,16,32,64,128,256]`, `fracs=[1.0]` (Arrhythmia also gets `fracs=[1,0.75,0.5,0.33,0.25]`):

| dataset | n | p | k≤n (harm regime reached) |
|---|--:|--:|---|
| arrhythmia (bridge) | 452 | 279 | 1,2,4,8,16,32,64,128,256 (all) |
| prostate_ge | 102 | 5,966 | 1,2,4,8,16,32,64 |
| arcene | 200 | 10,000 | 1,2,4,8,16,32,64,128 |
| gli85 | 85 | 22,283 | 1,2,4,8,16,32,64 |

Every set is probed from **k=1 (the common harm anchor)** up; low k sit well below n. Contrast is "same k, different p" (44→279→6k→22k). Non-degenerate, unlike the fracs grid.

## Run
- k=1 added as pre-specified; 512 dropped. Arrhythmia carries both protocols (k-grid + standard fracs) for the overlap check.
- **calibrate=none = headline protocol** (the main-finding arm; calibrated addendum can follow like diabetes130 if you want it).
- Same protocol otherwise byte-identical (REPS=30, 5 folds, 3 rankers, 3 learners, metrics, leakage firewall). New config `calibration_highdim.json[_arrhythmia]` — separate artifact, new hash, NOT merged (R6).
- **Order: smallest-p first** (arrhythmia → prostate_ge → arcene → gli85), sequential so results land early and the extreme corner is last; detached, resumable, startup-guarded. RAM safe alongside the diabetes130 addendum.
- Loader `src/nsclinfs/highdim_data.py` (frozen `data.py` untouched; registered only in `experiments/run_highdim.py`).

## Provenance (your §2 — recorded in `highdim_fetch_manifest.json`)
Per dataset: cited source of record = **original study** (Arcene=Guyon/NIPS-2003+UCI CC BY 4.0; Arrhythmia=UCI id5; Prostate-GE=Singh 2002; GLI-85=Freije 2004; SMK-CAN-187=Spira 2007), scikit-feature .mat = convenience mirror only (never cited), + sha256 + download URL used. GEO accessions marked "confirm" for the three microarray sets — I'll finalize the exact accessions and update the manifest.

Next heartbeat as each dataset completes (smallest first). Then RESULTS_tier2 with the boundary table.
