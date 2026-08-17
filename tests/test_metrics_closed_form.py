"""Closed-form checks for net benefit and the fairness gap -- no dataset required."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nsclinfs.fairness import auroc_gap
from nsclinfs.metrics import mean_net_benefit, net_benefit


def test_net_benefit_closed_form():
    # 4 patients: y = [1,1,0,0], p = [0.9, 0.4, 0.8, 0.1]; at t=0.5: pred=[1,0,1,0]
    y = np.array([1, 1, 0, 0]); p = np.array([0.9, 0.4, 0.8, 0.1])
    nb = net_benefit(y, p, np.array([0.5]))[0]
    assert abs(nb - (1 / 4 - 1 / 4 * (0.5 / 0.5))) < 1e-12   # TP/n - FP/n * t/(1-t) = 0


def test_net_benefit_perfect_model_equals_prevalence():
    y = np.array([1, 0, 1, 0, 0]); p = y.astype(float)
    ts = np.linspace(0.05, 0.5, 19)
    assert np.allclose(net_benefit(y, p, ts), y.mean())


def test_net_benefit_treat_none_is_zero():
    y = np.array([1, 0, 1, 0]); p = np.zeros(4)
    ts = np.array([0.1, 0.3])
    assert np.allclose(net_benefit(y, p, ts), 0.0)


def test_treat_all_formula():
    y = np.array([1, 0, 0, 0]); p = np.ones(4)          # predict everyone positive
    prev = y.mean()
    for t in (0.1, 0.25, 0.4):
        nb = net_benefit(y, p, np.array([t]))[0]
        assert abs(nb - (prev - (1 - prev) * t / (1 - t))) < 1e-12


def test_mean_net_benefit_honors_grid_args():
    """The config-driven grid must actually change the summary value (guards against the
    config knob becoming decorative) while the default reproduces the submitted 19-point
    0.05-0.5 definition."""
    rng = np.random.default_rng(0)
    y = (rng.random(500) < 0.3).astype(int)
    p = np.clip(rng.random(500) * 0.6 + y * 0.3, 0, 1)
    default = mean_net_benefit(y, p)
    explicit = mean_net_benefit(y, p, 0.05, 0.5, 19)
    assert default == explicit
    narrow = mean_net_benefit(y, p, 0.1, 0.3, 5)
    assert narrow != default


def test_auroc_gap_two_group_synthetic():
    rng = np.random.default_rng(1)
    n = 4000
    g = np.array(["a"] * (n // 2) + ["b"] * (n // 2))
    y = (rng.random(n) < 0.5).astype(int)
    p = np.where(y == 1, 0.8, 0.2) + rng.normal(0, 0.05, n)   # near-perfect in group a
    p_b = np.where(y == 1, 0.55, 0.45) + rng.normal(0, 0.2, n)  # weak in group b
    p = np.where(g == "a", p, p_b)
    import pandas as pd
    gap = auroc_gap(y, np.clip(p, 0, 1), pd.Series(g))
    assert gap > 0.1                                    # a real gap is detected
    gap0 = auroc_gap(y, np.clip(np.where(y == 1, 0.8, 0.2), 0, 1), pd.Series(g))
    assert abs(gap0) < 0.02                             # identical groups -> ~no gap
