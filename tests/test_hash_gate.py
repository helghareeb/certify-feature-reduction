"""R6 enforcement: the hash gate must REFUSE, not warn. These tests exist because
assert_single_hash spent v1 as dead code while the manuscript claimed enforcement."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from nsclinfs.hashing import CalibrationHashMismatch, assert_single_hash


def test_single_hash_passes():
    assert assert_single_hash(["abc", "abc", "abc"]) == "abc"


def test_two_hashes_refused():
    with pytest.raises(CalibrationHashMismatch):
        assert_single_hash(["abc", "def"])


def test_empty_refused():
    with pytest.raises(CalibrationHashMismatch):
        assert_single_hash([])
    with pytest.raises(CalibrationHashMismatch):
        assert_single_hash(["", None])


def test_aggregator_refuses_foreign_raw(tmp_path):
    """do_aggregate must refuse a raw CSV produced under a different calibration."""
    from run_clinical_fs import do_aggregate
    calib = {"REPS": 1, "outcomes": ["auroc"], "reference_frac": 1.0, "stat_alpha": 0.05,
             "RANDOM_SEED": 1, "fracs": [1.0]}
    raw = pd.DataFrame({"dataset": ["d"], "method": ["m"], "classifier": ["c"],
                        "calibrate": ["none"], "frac": [1.0], "rep": [0], "auroc": [0.5],
                        "calib_sha256": ["not-this-configs-hash"]})
    p = tmp_path / "raw.csv"
    raw.to_csv(p, index=False)
    with pytest.raises(SystemExit, match="refusing to aggregate"):
        do_aggregate(calib, str(p), str(tmp_path / "out.csv"))


def test_figure_loader_refuses_mixed(tmp_path):
    from make_figures import _load
    df = pd.DataFrame({"frac": [1.0, 0.25], "outcome": ["auroc"] * 2,
                       "calib_sha256": ["aaa", "bbb"]})
    p = tmp_path / "summary.csv"
    df.to_csv(p, index=False)
    with pytest.raises(CalibrationHashMismatch):
        _load(str(p))
