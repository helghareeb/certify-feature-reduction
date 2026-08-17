#!/usr/bin/env bash
cd <repo root> || exit 1
export XNSVAD_LOW_PRIORITY=1; PY=python
LOG=results/highdim/ag_driver.log
echo "===== arcene+gli85 START $(date '+%F %T') =====" >> "$LOG"
for d in arcene gli85; do
  grep -qE "AG_DONE $d" "$LOG" 2>/dev/null && { echo "skip $d" >> "$LOG"; continue; }
  echo "----- $d start $(date '+%T') -----" >> "$LOG"
  PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "$PY" experiments/run_highdim.py \
    --calib config/calibration_highdim.json --datasets "$d" --calibrations none \
    --out results/highdim/summary_$d.csv --raw results/highdim/raw_$d.csv >> results/highdim/log_$d.log 2>&1
  "$PY" experiments/run_highdim.py --calib config/calibration_highdim.json --datasets "$d" --aggregate-only \
    --out results/highdim/summary_$d.csv --raw results/highdim/raw_$d.csv >> results/highdim/log_$d.log 2>&1
  echo "AG_DONE $d rc=$? $(date '+%T') rawrows=$(grep -vcE '^#' results/highdim/raw_$d.csv 2>/dev/null)" >> "$LOG"
done
echo "===== arcene+gli85 ALL_DONE $(date '+%F %T') =====" >> "$LOG"
