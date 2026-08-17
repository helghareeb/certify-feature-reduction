"""Deterministic per-cell seed derivation (rule R5).

Every experiment cell (mechanism, rate, system, trial) receives a reproducible
32-bit seed derived from the master seed plus a canonicalised cell key, so each
seeded missingness-injection instance is byte-for-byte reproducible and a recorded
cross-seed sequence is available for cross-seed variance (N9).
"""
from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

import numpy as np

_SEED_MOD: int = 2**32


def _canonical(cell: Mapping[str, Any]) -> str:
    return "|".join(f"{k}={cell[k]}" for k in sorted(cell))


def derive_seed(master_seed: int, cell: Mapping[str, Any]) -> int:
    payload = f"{int(master_seed)}::{_canonical(cell)}".encode()
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % _SEED_MOD


def rng(master_seed: int, cell: Mapping[str, Any]) -> np.random.Generator:
    return np.random.default_rng(derive_seed(master_seed, cell))


def seed_sequence(master_seed: int, n: int) -> list[int]:
    return [derive_seed(master_seed, {"rep": i}) for i in range(n)]
