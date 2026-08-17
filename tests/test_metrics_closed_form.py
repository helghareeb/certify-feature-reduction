"""Closed-form checks for net benefit and the fairness gap -- no dataset required."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nsclinfs.fairness import auroc_gap
from nsclinfs.metrics import (
    brier_score_loss,
    expected_calibration_error,
    mean_net_benefit,
    mean_net_benefit_treat_all,
    murphy_decomposition,
    net_benefit,
    net_benefit_treat_all,
)


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


def test_treat_all_reference_matches_the_model_that_treats_everyone():
    """`net_benefit_treat_all` must agree with running `net_benefit` on p == 1."""
    y = np.array([1, 0, 0, 0, 1, 0, 0])
    ts = np.linspace(0.05, 0.5, 19)
    assert np.allclose(net_benefit_treat_all(y.mean(), ts), net_benefit(y, np.ones(len(y)), ts))
    assert abs(mean_net_benefit_treat_all(y.mean())
               - mean_net_benefit(y, np.ones(len(y)))) < 1e-12


def test_treat_all_beats_treat_none_exactly_below_prevalence():
    """The threshold at which treat-all stops paying is the prevalence itself, which is why a
    range lying entirely below prevalence is a range in which treat-all is hard to beat."""
    prev = 0.7
    assert net_benefit_treat_all(prev, np.array([prev]))[0] < 1e-12
    assert net_benefit_treat_all(prev, np.array([prev - 0.1]))[0] > 0.0     # treat-all pays
    assert net_benefit_treat_all(prev, np.array([prev + 0.1]))[0] < 0.0     # treat-none pays


def test_murphy_decomposition_reconstructs_the_binned_brier_score():
    """reliability - resolution + uncertainty == Brier of the bin-mean forecast, exactly, and the
    residual against the unbinned Brier score is reported rather than absorbed."""
    rng = np.random.default_rng(3)
    for n, rate in ((500, 0.3), (2000, 0.11), (300, 0.8)):
        y = (rng.random(n) < rate).astype(int)
        p = np.clip(rng.random(n) * 0.7 + y * 0.25, 0, 1)
        d = murphy_decomposition(y, p)
        assert abs(d["reliability"] - d["resolution"] + d["uncertainty"]
                   - d["brier_binned"]) < 1e-12
        assert abs(d["brier"] - brier_score_loss(y, p)) < 1e-12
        assert abs(d["binning_residual"] - (d["brier"] - d["brier_binned"])) < 1e-12


def test_murphy_decomposition_is_exact_when_the_forecast_is_already_binned():
    """With one predicted value per bin there is nothing for the binning to discard, so the
    classical identity closes against the true Brier score."""
    rng = np.random.default_rng(11)
    y = (rng.random(3000) < 0.4).astype(int)
    levels = np.array([0.1, 0.3, 0.5, 0.7, 0.9])          # each lands in its own 15-width bin
    p = levels[rng.integers(0, len(levels), len(y))]
    d = murphy_decomposition(y, p)
    assert abs(d["binning_residual"]) < 1e-12
    assert abs(d["reliability"] - d["resolution"] + d["uncertainty"]
               - brier_score_loss(y, p)) < 1e-12


def test_a_base_rate_constant_predictor_is_calibrated_and_has_no_resolution():
    """The degenerate case the decomposition exists to expose: a model that predicts the base
    rate for everyone scores near-zero calibration error while carrying no information. ECE
    cannot tell it apart from a good model; resolution can."""
    rng = np.random.default_rng(4)
    y = (rng.random(4000) < 0.12).astype(int)
    constant = np.full(len(y), y.mean())
    informative = np.clip(0.12 + (y * 2 - 1) * 0.08 + rng.normal(0, 0.01, len(y)), 0, 1)

    flat = murphy_decomposition(y, constant)
    good = murphy_decomposition(y, informative)

    assert expected_calibration_error(y, constant) < 1e-9        # perfectly calibrated
    assert flat["resolution"] < 1e-9                             # and perfectly uninformative
    assert good["resolution"] > 100 * max(flat["resolution"], 1e-12)
    assert flat["n_occupied"] == 1 and flat["largest_bin_share"] == 1.0


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
