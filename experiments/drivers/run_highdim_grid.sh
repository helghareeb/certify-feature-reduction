#!/usr/bin/env bash
# Tier-2 boundary arm: absolute-k grid on 4 datasets, SMALLEST-p FIRST (his order: early results, extreme last).
# calibrate=none = the headline protocol (main finding); calibrated addendum can follow. Resumable per dataset.
# Sequential so it is RAM-safe alongside the diabetes130 calibrated addendum (also running, low-priority).
cd <repo root> || exit 1
export HF_HOME=C:/research/_hf; export XNSVAD_LOW_PRIORITY=1
PY=python
mkdir -p results/highdim
LOG=results/highdim/driver.log
echo "===== highdim grid START $(date '+%F %T') =====" >> "$LOG"
# dataset : config  (smallest-p first)
run_ds () {
  local d="$1" cfg="$2"
  if grep -qE "ALL_REPS_DONE $d" "$LOG" 2>/dev/null; then echo "skip $d (done)" >> "$LOG"; return; fi
  echo "----- $d start $(date '+%T') cfg=$cfg -----" >> "$LOG"
  PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "$PY" experiments/run_highdim.py \
    --calib "$cfg" --datasets "$d" --calibrations none \
    --out "results/highdim/summary_$d.csv" --raw "results/highdim/raw_$d.csv" >> "results/highdim/log_$d.log" 2>&1
  rc=$?
  ac=$("$PY" experiments/run_highdim.py --calib "$cfg" --datasets "$d" --aggregate-only \
       --out "results/highdim/summary_$d.csv" --raw "results/highdim/raw_$d.csv" >> "results/highdim/log_$d.log" 2>&1; echo done)
  echo "ALL_REPS_DONE $d rc=$rc $(date '+%T') rawrows=$(grep -vcE '^#' results/highdim/raw_$d.csv 2>/dev/null)" >> "$LOG"
}
run_ds arrhythmia  config/calibration_highdim_arrhythmia.json
run_ds prostate_ge config/calibration_highdim.json
run_ds arcene      config/calibration_highdim.json
run_ds gli85       config/calibration_highdim.json
echo "===== highdim grid ALL_DONE $(date '+%F %T') =====" >> "$LOG"
