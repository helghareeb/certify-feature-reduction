"""The v2 budget arm on a synthetic dataset: seed pairing across budgets, exact-k dedupe
bitwise identity, k >= p skipping, and Holm family isolation between budget types."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from nsclinfs.run import run_grid


def _toy(n=120, p=4, seed=0):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(rng.normal(size=(n, p)), columns=[f"f{i}" for i in range(p)])
    y = (X["f0"] + 0.5 * X["f1"] + rng.normal(0, 0.5, n) > 0).astype(int).to_numpy()
    sens = pd.Series(np.where(rng.random(n) < 0.5, "a", "b"), name="g")
    return X, y, sens


def _grid(budgets):
    X, y, sens = _toy()
    return run_grid(X, y, sens, budgets=budgets, methods=["mutual_info"],
                    classifiers=["logistic"], n_reps=2, master_seed=7, n_folds=3,
                    dataset="toy")


def test_seed_constant_across_budgets():
    raw = _grid({"fracs": [1.0, 0.5, 0.25], "ks": [1, 2]})
    for (_, _, _, rep), g in raw.groupby(["dataset", "method", "classifier", "rep"]):
        assert g["seed"].nunique() == 1


def test_exact_k_dedupe_bitwise():
    """frac 0.25 on p=4 gives k=1; the explicit k:1 level must be the SAME model."""
    raw = _grid({"fracs": [1.0, 0.25], "ks": [1]})
    metrics = [c for c in raw.columns if c not in
               ("budget_type", "budget", "frac", "rep", "seed", "runtime_s")]
    for rep, g in raw.groupby("rep"):
        a = g[g["budget"] == "frac:0.25"][metrics].reset_index(drop=True)
        b = g[g["budget"] == "k:1"][metrics].reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)


def test_k_at_or_above_p_skipped():
    raw = _grid({"fracs": [1.0], "ks": [4, 8]})         # p=4 -> both skipped
    assert set(raw["budget"]) == {"frac:1"}


def test_k_features_column():
    raw = _grid({"fracs": [1.0, 0.5], "ks": [2]})
    assert (raw[raw["budget"] == "frac:0.5"]["k_features"] == 2).all()
    assert (raw[raw["budget"] == "k:2"]["k_features"] == 2).all()
    assert (raw[raw["budget"] == "frac:1"]["k_features"] == 4).all()


def test_holm_family_isolation():
    """Adding the exact-k arm must not move p_holm of the frac comparisons."""
    from run_clinical_fs import aggregate
    raw_both = _grid({"fracs": [1.0, 0.5, 0.25], "ks": [1, 2, 3]})
    raw_frac = raw_both[raw_both["budget_type"] == "frac"].copy()
    kw = dict(outcomes=["auroc", "aurc"], ref=1.0, alpha=0.05, seed=7)
    s_both = aggregate(raw_both, **kw)
    s_frac = aggregate(raw_frac, **kw)
    a = (s_both[s_both["budget_type"] == "frac"]
         .set_index(["budget", "outcome"])["p_holm"].dropna().sort_index())
    b = s_frac.set_index(["budget", "outcome"])["p_holm"].dropna().sort_index()
    pd.testing.assert_series_equal(a, b)
