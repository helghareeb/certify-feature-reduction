"""Content hashing of the calibration config and the CSV hash-gate (rule R6).

The calibration JSON is content-hashed (SHA-256 over its canonical serialisation);
the hash is embedded in every results CSV header and in the data MANIFEST.
Downstream analysis refuses to combine rows whose calibration hashes differ, so
two incompatible pipelines can never be silently merged.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

CALIB_HASH_KEY: str = "calib_sha256"


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_hash(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def hash_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class CalibrationHashMismatch(ValueError):
    """Raised when results carrying different calibration hashes are combined."""


def assert_single_hash(hashes: Iterable[str]) -> str:
    uniq = sorted({h for h in hashes if h})
    if len(uniq) == 0:
        raise CalibrationHashMismatch("no calibration hash present in inputs")
    if len(uniq) > 1:
        raise CalibrationHashMismatch(
            f"refusing to combine rows with differing calibration hashes: {uniq}"
        )
    return uniq[0]
