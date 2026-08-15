"""Subgroup (fairness) gaps: the spread of a metric across protected groups.

The gap is max-min of a per-group metric, so a larger gap = more disparity. We
report gaps for discrimination (AUROC), calibration (ECE), and selective risk so
the audit can ask whether aggressive reduction widens any of them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .metrics import conformal_covered, expected_calibration_error, mean_net_benefit


def _per_group(y, p, sensitive, fn) -> dict:
    out = {}
    s = pd.Series(sensitive).reset_index(drop=True)
    y = np.asarray(y); p = np.asarray(p)
    for g in sorted(s.dropna().unique()):
        m = (s == g).to_numpy()
        if m.sum() < 10 or len(np.unique(y[m])) < 2:
            continue
        out[str(g)] = float(fn(y[m], p[m]))
    return out


def _gap(per_group: dict) -> float:
    vals = list(per_group.values())
    return float(max(vals) - min(vals)) if len(vals) >= 2 else float("nan")


def auroc_gap(y, p, sensitive) -> float:
    return _gap(_per_group(y, p, sensitive, lambda yy, pp: roc_auc_score(yy, pp)))


def ece_gap(y, p, sensitive) -> float:
    return _gap(_per_group(y, p, sensitive, lambda yy, pp: expected_calibration_error(yy, pp)))


def net_benefit_gap(y, p, sensitive) -> float:
    """Subgroup net-benefit parity: max-min of the mean decision-curve net benefit across groups
    (larger = more disparity in realised clinical utility)."""
    return _gap(_per_group(y, p, sensitive, lambda yy, pp: mean_net_benefit(yy, pp)))


def conformal_coverage_gap(y, p, sensitive, alpha: float = 0.1) -> float:
    """Group-conditional coverage gap: with one MARGINAL conformal threshold, the max-min of
    realised coverage across protected groups (larger = some groups under-covered = less fair).
    Marginal coverage is ~1-alpha by construction, so a positive gap is a pure equity signal."""
    covered, _ = conformal_covered(y, p, alpha)
    s = pd.Series(sensitive).reset_index(drop=True)
    per = {}
    for g in sorted(s.dropna().unique()):
        m = (s == g).to_numpy()
        if m.sum() < 10:
            continue
        per[str(g)] = float(covered[m].mean())
    return _gap(per)
