#!/usr/bin/env bash
# TIER 7 — vary n at FIXED p=279 (arrhythmia), to disentangle the n/p confound in the Tier-2 boundary.
# Runs n=100,150,250 fresh; n=452 (full) reuses the existing summary_arrhythmia.csv (identical protocol).
# Sequential, resumable per-n, low-priority, own log. QUEUED: launched only after Tier 6 completes.
cd <repo root> || exit 1
export HF_HOME=C:/research/_hf; export XNSVAD_LOW_PRIORITY=1
PY=python
mkdir -p results/tier7
LOG=results/tier7/tier7_driver.log
echo "===== tier7 (n/p disentangle) START $(date '+%F %T') =====" >> "$LOG"
run_n () {
  local n="$1"
  if grep -qE "TIER7_DONE n=$n" "$LOG" 2>/dev/null; then echo "skip n=$n (done)" >> "$LOG"; return; fi
  echo "----- n=$n start $(date '+%T') -----" >> "$LOG"
  PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "$PY" experiments/run_highdim.py \
    --calib "config/calibration_tier7_n${n}.json" --datasets arrhythmia --calibrations none \
    --out "results/tier7/summary_arrhythmia_n${n}.csv" --raw "results/tier7/raw_arrhythmia_n${n}.csv" \
    >> "results/tier7/log_n${n}.log" 2>&1
  rc=$?
  "$PY" experiments/run_highdim.py --calib "config/calibration_tier7_n${n}.json" --datasets arrhythmia \
    --aggregate-only --out "results/tier7/summary_arrhythmia_n${n}.csv" \
    --raw "results/tier7/raw_arrhythmia_n${n}.csv" >> "results/tier7/log_n${n}.log" 2>&1
  echo "TIER7_DONE n=$n rc=$rc $(date '+%T') rawrows=$(grep -vcE '^#' results/tier7/raw_arrhythmia_n${n}.csv 2>/dev/null)" >> "$LOG"
}
run_n 100
run_n 150
run_n 250
echo "===== tier7 ALL_DONE $(date '+%F %T') =====" >> "$LOG"
