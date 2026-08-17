"""Fetch every raw dataset from its pinned source URL and verify it by SHA-256.

Usage:
    PYTHONPATH=src python experiments/fetch_data.py                # fetch missing, verify all
    PYTHONPATH=src python experiments/fetch_data.py --verify-only  # no network; verify what exists
    PYTHONPATH=src python experiments/fetch_data.py --write-manifest
        # (first run / deliberate repin) record the hashes of the files now on disk

The pin file is data/MANIFEST.json: {dataset: {filename: {url, sha256, bytes}}}.
Raw files stay gitignored; only the manifest is committed. `wdbc` ships with
scikit-learn and needs no entry. A hash mismatch is an error, never a warning:
a silently different raw file would change results while every config hash
still matched (the one provenance hole the calibration hash cannot see).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "MANIFEST.json"

# dataset -> {target filename under data/<dataset>/raw/ : source URL}
SOURCES: dict[str, dict[str, str]] = {
    "cleveland": {
        "processed.cleveland.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
    },
    "pima": {
        "pima.csv": "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv",
    },
    "ilpd": {
        "ilpd.csv": "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv",
    },
    "heartfailure": {
        "heartfailure.csv": "https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv",
    },
    "statlogheart": {
        "heart.dat": "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/heart/heart.dat",
    },
    "haberman": {
        "haberman.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/haberman/haberman.data",
    },
    "hepatitis": {
        "hepatitis.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/hepatitis/hepatitis.data",
    },
    "mammographic": {
        "mammographic_masses.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/mammographic-masses/mammographic_masses.data",
    },
    "bcw": {
        "breast-cancer-wisconsin.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data",
    },
    "spectf": {
        "SPECTF.train": "https://archive.ics.uci.edu/ml/machine-learning-databases/spect/SPECTF.train",
        "SPECTF.test": "https://archive.ics.uci.edu/ml/machine-learning-databases/spect/SPECTF.test",
    },
    "diabetes130": {
        "dataset_diabetes.zip": "https://archive.ics.uci.edu/ml/machine-learning-databases/00296/dataset_diabetes.zip",
    },
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "certify-feature-reduction fetch_data/1.0"})
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.replace(dest)


def unzip_diabetes(raw_dir: Path) -> None:
    z = raw_dir / "dataset_diabetes.zip"
    target = raw_dir / "dataset_diabetes" / "diabetic_data.csv"
    if z.exists() and not target.exists():
        with zipfile.ZipFile(z) as zf:
            zf.extractall(raw_dir)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true", help="no network; verify files on disk against the manifest")
    ap.add_argument("--write-manifest", action="store_true", help="record hashes of files currently on disk (first run / deliberate repin)")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    failures, fetched, verified = [], 0, 0

    for ds, files in SOURCES.items():
        raw_dir = ROOT / "data" / ds / "raw"
        for fname, url in files.items():
            dest = raw_dir / fname
            pin = manifest.get(ds, {}).get(fname)
            if not dest.exists():
                if args.verify_only:
                    failures.append(f"{ds}/{fname}: MISSING (verify-only, not fetched)")
                    continue
                print(f"fetching {ds}/{fname} ...")
                try:
                    fetch(url, dest)
                    fetched += 1
                except Exception as e:  # noqa: BLE001 - report and continue to surface all failures at once
                    failures.append(f"{ds}/{fname}: FETCH FAILED: {e}")
                    continue
            digest = sha256_of(dest)
            if pin is None:
                if args.write_manifest:
                    manifest.setdefault(ds, {})[fname] = {"url": url, "sha256": digest, "bytes": dest.stat().st_size}
                    print(f"pinned  {ds}/{fname}  {digest[:16]}…")
                else:
                    failures.append(f"{ds}/{fname}: no pin in MANIFEST.json (run --write-manifest deliberately)")
            elif digest != pin["sha256"]:
                failures.append(f"{ds}/{fname}: HASH MISMATCH disk={digest[:16]}… pinned={pin['sha256'][:16]}…")
            else:
                verified += 1
    unzip_diabetes(ROOT / "data" / "diabetes130" / "raw")

    if args.write_manifest:
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(f"wrote {MANIFEST}")
    print(f"fetched={fetched} verified={verified} failures={len(failures)}")
    for f in failures:
        print("  FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
