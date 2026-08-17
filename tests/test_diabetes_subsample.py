"""Config-driven Diabetes-130 loader: n_target honored, joint stratification preserves the
race distribution (the v1 comment claimed this while the code did not do it), null = full
cohort, fixed seed = identical index. Needs the raw file (fetch_data.py); skips cleanly
without it."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

RAW = ROOT / "data" / "diabetes130" / "raw"
pytestmark = pytest.mark.skipif(
    not (RAW / "dataset_diabetes" / "diabetic_data.csv").exists()
    and not list(RAW.rglob("diabetic_data.csv")) if RAW.exists() else True,
    reason="diabetes130 raw not fetched (run experiments/fetch_data.py)")

from nsclinfs.data import load_diabetes130  # noqa: E402


def test_full_cohort_when_null():
    X, y, race = load_diabetes130(params={"n_target": None})
    assert len(X) == 101763            # post gender-filter cohort
    assert X.shape[1] == 16


def test_v1_default_reproduced():
    X, y, race = load_diabetes130()    # defaults = the v1 submission's subsample
    assert len(X) == 6000 or len(X) == 5999  # per-stratum rounding may drop one row
    assert abs(y.mean() - 0.112) < 0.01


def test_joint_stratification_preserves_race():
    Xf, yf, rf = load_diabetes130(params={"n_target": None})
    Xs, ys, rs = load_diabetes130(params={"n_target": 6000, "stratify": "outcome_race",
                                          "subsample_seed": 20260626})
    full = rf.value_counts(normalize=True)
    sub = rs.value_counts(normalize=True)
    for grp, frac in full.items():
        if frac > 0.01:               # groups big enough for the guarantee to bind
            assert abs(sub.get(grp, 0.0) - frac) < 0.01, grp
    assert abs(ys.mean() - yf.mean()) < 0.01


def test_subsample_deterministic():
    a = load_diabetes130(params={"n_target": 3000, "stratify": "outcome_race"})[0]
    b = load_diabetes130(params={"n_target": 3000, "stratify": "outcome_race"})[0]
    assert (a.index == b.index).all()
    assert np.allclose(a.to_numpy(), b.to_numpy(), equal_nan=True)
