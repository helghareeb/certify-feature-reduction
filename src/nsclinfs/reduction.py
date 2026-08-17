"""Feature-reduction strategies, fit on TRAIN ONLY (leakage firewall).

Each `rank(X_train, y_train, seed)` returns ALL feature names ordered best-first by a
standard, published importance criterion; the audit keeps the top-k (k = round(frac*p)).
Computing the full ranking once per fold and slicing per fraction is exact and avoids
refitting the selector for every reduction level.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression


def _order(scores: np.ndarray, cols) -> list[str]:
    idx = np.argsort(-np.asarray(scores, dtype=float), kind="mergesort")
    return [cols[i] for i in idx]


def rank_mutual_info(X: pd.DataFrame, y: np.ndarray, seed: int) -> list[str]:
    mi = mutual_info_classif(X.fillna(X.median(numeric_only=True)), y, random_state=seed)
    return _order(mi, list(X.columns))


def rank_rf_importance(X: pd.DataFrame, y: np.ndarray, seed: int) -> list[str]:
    rf = RandomForestClassifier(n_estimators=80, random_state=seed, n_jobs=1)
    rf.fit(X.fillna(X.median(numeric_only=True)), y)
    return _order(rf.feature_importances_, list(X.columns))


def rank_l1_logistic(X: pd.DataFrame, y: np.ndarray, seed: int) -> list[str]:
    Xi = X.fillna(X.median(numeric_only=True))
    Xs = (Xi - Xi.mean()) / Xi.std(ddof=0).replace(0.0, 1.0)
    lr = LogisticRegression(penalty="l1", solver="liblinear", C=0.5, random_state=seed, max_iter=2000)
    lr.fit(Xs, y)
    return _order(np.abs(lr.coef_.ravel()), list(X.columns))


RANKERS = {
    "mutual_info": rank_mutual_info,
    "rf_importance": rank_rf_importance,
    "l1_logistic": rank_l1_logistic,
}


def retained_k(frac: float, n_features: int) -> int:
    """The budget rule: how many features a fractional budget retains.

    max(1, round(frac * p)) with Python's banker's rounding — the exact rule the v1
    submission ran (formerly inline in run.py). Two properties are load-bearing and
    deliberately preserved, not "fixed": the floor means every budget keeps >=1 feature
    (so on p=3, the 0.33 and 0.25 budgets are the SAME one-feature model), and
    round-half-to-even means e.g. p=5 at frac 0.5 retains 2, not 3. Both are disclosed
    in the manuscript; changing either would silently move k for several datasets.
    """
    return max(1, int(round(frac * n_features)))


def rank(method: str, X: pd.DataFrame, y: np.ndarray, seed: int) -> list[str]:
    return RANKERS[method](X, y, seed)


def select(method: str, X: pd.DataFrame, y: np.ndarray, k: int, seed: int) -> list[str]:
    """Top-k by `method` (kept for tests / single-level use)."""
    return rank(method, X, y, seed)[: max(1, min(int(k), X.shape[1]))]
