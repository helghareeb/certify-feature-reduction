"""Chunked, resumable, multi-process launcher for the v2 grid (Stage 4 of the revision).

Enumerates shards from the config, skips shards whose output already exists with the
expected row count, and runs the rest as separate single-threaded subprocesses (every
model fit is already n_jobs=1; cross-process parallelism cannot affect determinism
because each cell derives its own seed). Diabetes-130 shards are further split into
rep-chunks and launched FIRST (longest pole); small datasets backfill idle workers.

    PYTHONPATH=src python experiments/launch_grid.py --calib config/calibration.json \
        --shard-dir results/raw/shards --max-workers 6

Re-running the launcher after a crash resumes: completed shards are skipped by row count.
Merging + aggregation happen afterwards in experiments/merge_shards.py, never here.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nsclinfs.reduction import retained_k  # noqa: E402

P_OF = {"cleveland": 12, "pima": 8, "ilpd": 9, "heartfailure": 11, "wdbc": 30,
        "statlogheart": 12, "haberman": 3, "hepatitis": 18, "mammographic": 5,
        "bcw": 9, "spectf": 44, "diabetes130": 16}
BIG = {"diabetes130"}
REP_CHUNK_BIG = 5


def n_levels(calib: dict, ds: str) -> int:
    b = calib.get("budgets")
    if not b:
        return len(calib["fracs"])
    return len(b["fracs"]) + sum(1 for k in b.get("ks", []) if k < P_OF[ds])


def shards(calib: dict):
    """Yield (name, only-filters, rep_start, rep_end, expected_rows). Big datasets first."""
    reps = int(calib["REPS"])
    cals = calib.get("calibrations", ["none"])
    datasets = sorted(calib["datasets"], key=lambda d: (d not in BIG, d))
    for ds in datasets:
        lv = n_levels(calib, ds)
        for m in calib["reduction_methods"]:
            if ds in BIG:
                for c in calib["classifiers"]:
                    for r0 in range(0, reps, REP_CHUNK_BIG):
                        r1 = min(r0 + REP_CHUNK_BIG, reps)
                        yield (f"{ds}__{m}__{c}__reps{r0}-{r1}",
                               {"datasets": [ds], "methods": [m], "classifiers": [c]},
                               r0, r1, lv * (r1 - r0) * len(cals))
            else:
                yield (f"{ds}__{m}__reps0-{reps}",
                       {"datasets": [ds], "methods": [m]},
                       0, reps, lv * reps * len(calib["classifiers"]) * len(cals))


def run_shard(py: str, calib_path: str, shard_dir: Path, name: str, only: dict,
              r0: int, r1: int) -> tuple[str, bool, float]:
    out = shard_dir / f"{name}.csv"
    cmd = [py, str(ROOT / "experiments" / "run_clinical_fs.py"), "--calib", calib_path,
           "--raw", str(out), "--rep-start", str(r0), "--rep-end", str(r1)]
    for key, flag in (("datasets", "--datasets"), ("methods", "--methods"),
                      ("classifiers", "--classifiers"), ("calibrations", "--calibrations")):
        if key in only:
            cmd += [flag, *only[key]]
    t = time.perf_counter()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       env={**__import__("os").environ, "PYTHONPATH": "src"})
    ok = r.returncode == 0
    if not ok:
        (shard_dir / f"{name}.err.log").write_text(r.stdout[-4000:] + "\n" + r.stderr[-4000:])
    return name, ok, time.perf_counter() - t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", default="config/calibration.json")
    ap.add_argument("--shard-dir", default="results/raw/shards")
    ap.add_argument("--max-workers", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    calib = json.loads((ROOT / a.calib).read_text())
    shard_dir = ROOT / a.shard_dir
    shard_dir.mkdir(parents=True, exist_ok=True)
    py = sys.executable

    todo, done = [], 0
    for name, only, r0, r1, expect in shards(calib):
        out = shard_dir / f"{name}.csv"
        if out.exists():
            try:
                import pandas as pd
                have = len(pd.read_csv(out))
            except Exception:
                have = -1
            if have == expect:
                done += 1
                continue
            out.unlink()                                # partial/corrupt shard: redo whole
        todo.append((name, only, r0, r1))
    print(f"[launch] {done} shards already complete, {len(todo)} to run, "
          f"{a.max_workers} workers")
    if a.dry_run or not todo:
        for t in todo:
            print("  would run:", t[0])
        return 0

    t0 = time.perf_counter()
    failures = []
    with ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        futs = {ex.submit(run_shard, py, a.calib, shard_dir, *t): t[0] for t in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            name, ok, dt = fut.result()
            print(f"[{i}/{len(todo)}] {'ok  ' if ok else 'FAIL'} {name}  {dt / 60:.1f} min  "
                  f"(elapsed {(time.perf_counter() - t0) / 3600:.2f} h)", flush=True)
            if not ok:
                failures.append(name)
    print(f"[launch] finished in {(time.perf_counter() - t0) / 3600:.2f} h; "
          f"{len(failures)} failures")
    for f in failures:
        print("  FAIL:", f, "->", shard_dir / f"{f}.err.log")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
