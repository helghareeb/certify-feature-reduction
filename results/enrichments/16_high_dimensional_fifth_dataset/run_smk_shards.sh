#!/usr/bin/env bash
# smk_can_187 5th high-dim dataset -- 9 shards (3 rankers x 3 learners) concurrent, then merge.
# Egyptian agent NOTE_parallelise recipe. n_jobs=1 in-estimator (never raised) -> bit-identical.
set -e
cd "$(dirname "$0")"
PY=/c/research/_env/nsclin/Scripts/python.exe
mkdir -p results/raw/shards_smk
for m in mutual_info rf_importance l1_logistic; do
  for c in logistic rf gb; do
    "$PY" experiments/run_highdim.py --calib config/calibration_highdim.json \
      --datasets smk_can_187 --methods "$m" --classifiers "$c" \
      --rep-start 0 --rep-end 30 \
      --raw results/raw/shards_smk/${m}__${c}.csv &
  done
done
wait
echo "=== all 9 shards done; merging ==="
"$PY" experiments/merge_shards.py --calib config/calibration_highdim.json --shard-dir results/raw/shards_smk
echo "=== smk shards merged ==="
