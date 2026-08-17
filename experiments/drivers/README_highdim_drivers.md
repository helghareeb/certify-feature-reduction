# High-dimensional arm -- drivers & loader (as they ran) -- 2026-08-16 00:50 AST
Closes the last code gap (REQUEST_highdim_code). Self-audit vs the 3 leakage questions at the end.

## Files
- **run_highdim.py** -- the driver: registers HIGHDIM_LOADERS into nsclinfs.data.LOADERS, then delegates
  to experiments/run_clinical_fs.main() (reads sys.argv). All per-fold work is the FROZEN in-fold firewall.
- **highdim_data.py** -- loaders for arcene/gli85/prostate_ge/smk_can_187/arrhythmia (read .mat / .data from
  <high-dimensional data directory>). load_arrhythmia also carries the SAME subsample convention as
  load_diabetes130 (n_target/stratify/seed) for Tier 7. (Byte-identical to the frozen copy already sent.)

## How each run was actually invoked (honest)
- arcene, gli85: **run_highdim_ag.sh** (own log ag_driver.log; arcene -> gli85 sequential). PRODUCED
  summary_arcene.csv, summary_gli85.csv.
- arrhythmia (full), prostate_ge: **run_highdim_grid.sh** (driver.log). PRODUCED summary_arrhythmia.csv,
  summary_prostate_ge.csv. (arcene/gli85 were blocked in this script via fake ALL_REPS_DONE markers so the
  _ag driver owned them -- that is why those two lines look skipped in driver.log.)
- Tier 7 (arrhythmia n=100/150/250): the ACTUAL run was an inline bash background loop calling
  run_highdim.py --calib config/calibration_tier7_n{N}.json --datasets arrhythmia, followed by a separate
  --aggregate-only pass (the summary is written only by the aggregate step). **run_tier7.sh / _run_tier7.cmd
  mirror that logic faithfully** but were not the exact processes that ran (the inline loop was); included
  for completeness and labelled as such.
- Each per-n / per-dataset run is config-driven; the config's content_hash is the calib_sha256 stamp
  (configs already shipped in calibration_configs_2026-08-15.zip).

## Self-audit (3 questions)
Q1 label-informed choice outside CV? NO -- run_highdim.py only registers loaders + delegates; selection/
ranking happen per training fold inside the frozen runner. Q2 all-rows statistic into a per-fold model? NO.
Q3 impute/rank/standardise train-fold-only? YES (frozen firewall). The arrhythmia subsample is stratified
on outcome with a fixed seed at LOAD time (defines the cohort, identical across reps; not a per-fold leak).
