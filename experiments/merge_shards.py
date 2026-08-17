"""Merge grid shards into the canonical raw CSV, verify, and aggregate (Stage 4 tail).

Asserts (a) every shard carries exactly ONE calibration hash and it is THIS config's hash,
(b) no duplicate (cell, budget, rep) rows across shards, (c) the merged row count equals
the config-implied expectation. Then writes results/raw/audit.csv, merges the per-shard
net-benefit curve parquets into results/cache/nb_curves.parquet, and runs the canonical
aggregation (R2).

    PYTHONPATH=src python experiments/merge_shards.py --calib config/calibration.json \
        --shard-dir results/raw/shards --out results/summary.csv
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from nsclinfs.hashing import CALIB_HASH_KEY, assert_single_hash, content_hash  # noqa: E402
from launch_grid import n_levels  # noqa: E402
from run_clinical_fs import do_aggregate  # noqa: E402

CELL = ["dataset", "method", "classifier", "calibrate", "budget", "rep"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", default="config/calibration.json")
    ap.add_argument("--shard-dir", default="results/raw/shards")
    ap.add_argument("--raw-out", default="results/raw/audit.csv")
    ap.add_argument("--out", default="results/summary.csv")
    ap.add_argument("--nb-out", default="results/cache/nb_curves.parquet")
    a = ap.parse_args()
    calib = json.loads((ROOT / a.calib).read_text())
    chash = content_hash(calib)
    shard_dir = ROOT / a.shard_dir

    csvs = sorted(shard_dir.glob("*.csv"))
    if not csvs:
        raise SystemExit(f"no shards in {shard_dir}")
    frames = [pd.read_csv(p) for p in csvs]
    raw = pd.concat(frames, ignore_index=True)
    got = assert_single_hash(raw[CALIB_HASH_KEY])
    if got != chash:
        raise SystemExit(f"shards carry hash {got[:12]}… but config hashes to {chash[:12]}…")

    dup = raw.duplicated(subset=CELL)
    if dup.any():
        raise SystemExit(f"{int(dup.sum())} duplicate (cell,budget,rep) rows across shards")

    reps = int(calib["REPS"])
    cals = len(calib.get("calibrations", ["none"]))
    combos = len(calib["reduction_methods"]) * len(calib["classifiers"])
    expect = sum(n_levels(calib, ds) * combos * cals * reps for ds in calib["datasets"])
    if len(raw) != expect:
        raise SystemExit(f"merged rows {len(raw)} != expected {expect}")

    out_raw = ROOT / a.raw_out
    out_raw.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out_raw, index=False)
    print(f"[merge] {len(csvs)} shards -> {len(raw)} rows -> {out_raw}")

    nbs = sorted(shard_dir.glob("*_nb_curves.parquet"))
    if nbs:
        nb = pd.concat([pd.read_parquet(p) for p in nbs], ignore_index=True)
        assert_single_hash(nb[CALIB_HASH_KEY])
        dest = ROOT / a.nb_out
        dest.parent.mkdir(parents=True, exist_ok=True)
        nb.to_parquet(dest, index=False)
        print(f"[merge] nb curves: {len(nb)} rows -> {dest}")

    do_aggregate(calib, str(out_raw), str(ROOT / a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
