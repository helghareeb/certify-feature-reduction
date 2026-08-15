"""Smoke + leakage-firewall + determinism tests."""
from pathlib import Path

import numpy as np
import pytest

from nsclinfs.data import load_cleveland
from nsclinfs.metrics import (
    aurc,
    conformal_coverage,
    conformal_efficiency,
    expected_calibration_error,
    mean_net_benefit,
    net_benefit,
    selective_ece,
)
from nsclinfs.run import run_cell

# Data-dependence is per-test, not module-wide: on a dataless clone the pure-metric tests
# must RUN (a fully-skipped suite reads as green while testing nothing).
_HAVE = (Path("data/cleveland/raw/processed.cleveland.data")).exists()
needs_cleveland = pytest.mark.skipif(not _HAVE, reason="Cleveland raw not downloaded "
                                     "(run experiments/fetch_data.py)")


def test_metrics_bounds():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 200)
    p = rng.random(200)
    assert 0.0 <= expected_calibration_error(y, p) <= 1.0
    assert np.isfinite(aurc(y, p, np.abs(p - 0.5)))


def test_new_metric_bounds():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 400)
    p = rng.random(400)
    # conformal marginal coverage must be ~nominal (1 - alpha = 0.9) by construction
    assert abs(conformal_coverage(y, p, alpha=0.1) - 0.9) < 0.05
    assert 1.0 <= conformal_efficiency(y, p) <= 2.0          # binary set size in [1, 2]
    assert 0.0 <= selective_ece(y, p) <= 1.0
    # net benefit of a perfect model exceeds that of a random one; bounded above by prevalence
    yp = (p > 0.5).astype(int)
    assert mean_net_benefit(yp.astype(float) * 0 + yp, yp.astype(float)) >= mean_net_benefit(y, p) - 1
    nb = net_benefit(y, p, np.array([0.2, 0.5]))
    assert np.all(np.isfinite(nb))


@needs_cleveland
def test_seed_determinism():
    X, y, s = load_cleveland()
    a = run_cell(X, y, s, frac=0.5, method="mutual_info", classifier="logistic", seed=123)
    b = run_cell(X, y, s, frac=0.5, method="mutual_info", classifier="logistic", seed=123)
    for k in ("auroc", "ece", "brier", "aurc", "auroc_gap"):
        assert a[k] == b[k], (k, a[k], b[k])


@needs_cleveland
def test_leakage_firewall_shuffled_labels():
    """With labels shuffled before the whole pipeline, a leakage-free fit must score
    ~chance: any in-fold selection/scaling/fitting cannot manufacture signal."""
    X, y, s = load_cleveland()
    aurocs = []
    for seed in range(5):
        yp = np.random.default_rng(seed).permutation(y)
        r = run_cell(X, yp, s, frac=0.5, method="mutual_info", classifier="logistic", seed=seed)
        aurocs.append(r["auroc"])
    assert abs(float(np.mean(aurocs)) - 0.5) < 0.08, float(np.mean(aurocs))
