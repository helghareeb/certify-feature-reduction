"""Evaluation metrics: predictive, calibration, and selective prediction.

`p` is always the predicted probability of the positive (event) class.
`confidence` is a per-sample certainty score (higher = keep, lower = abstain); here it is
the margin |p-0.5|, used to order predictions for the risk--coverage / AURC computation.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    roc_auc_score,
)


def expected_calibration_error(y: np.ndarray, p: np.ndarray, bins: int = 15) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    ece = 0.0
    n = len(y)
    for b in range(bins):
        m = idx == b
        if not m.any():
            continue
        conf = p[m].mean()
        acc = y[m].mean()
        ece += (m.sum() / n) * abs(acc - conf)
    return float(ece)


def predictive_metrics(y: np.ndarray, p: np.ndarray, threshold: float = 0.5) -> dict:
    yhat = (p >= threshold).astype(int)
    out = {
        "accuracy": float((yhat == y).mean()),
        "f1_macro": float(f1_score(y, yhat, average="macro", zero_division=0)),
        "brier": float(brier_score_loss(y, p)),
        "ece": expected_calibration_error(y, p),
    }
    # AUROC/AUPRC need both classes present.
    if len(np.unique(y)) == 2:
        out["auroc"] = float(roc_auc_score(y, p))
        out["auprc"] = float(average_precision_score(y, p))
    else:
        out["auroc"] = float("nan")
        out["auprc"] = float("nan")
    return out


def risk_coverage(y: np.ndarray, p: np.ndarray, confidence: np.ndarray,
                  threshold: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """Risk (error rate on retained) vs coverage, sweeping the confidence cutoff.

    Samples are retained from most- to least-confident; risk is the 0/1 error of
    the thresholded prediction on the retained set.
    """
    yhat = (p >= threshold).astype(int)
    err = (yhat != y).astype(float)
    order = np.argsort(-confidence, kind="mergesort")  # most confident first
    err_sorted = err[order]
    n = len(y)
    coverages = np.arange(1, n + 1) / n
    risks = np.cumsum(err_sorted) / np.arange(1, n + 1)
    return coverages, risks


def aurc(y: np.ndarray, p: np.ndarray, confidence: np.ndarray,
         threshold: float = 0.5) -> float:
    """Area under the risk-coverage curve (lower is better)."""
    cov, risk = risk_coverage(y, p, confidence, threshold)
    return float(np.trapezoid(risk, cov))


def selective_at_coverage(y: np.ndarray, p: np.ndarray, confidence: np.ndarray,
                          coverage: float, threshold: float = 0.5) -> dict:
    """Accuracy/risk when retaining the top-`coverage` fraction by confidence."""
    n = len(y)
    k = max(1, int(round(coverage * n)))
    order = np.argsort(-confidence, kind="mergesort")[:k]
    yhat = (p[order] >= threshold).astype(int)
    return {
        "coverage": k / n,
        "selective_accuracy": float((yhat == y[order]).mean()),
        "selective_risk": float((yhat != y[order]).mean()),
    }


def net_benefit(y: np.ndarray, p: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Decision-curve net benefit at each threshold: NB(t) = TP/n - (FP/n)*t/(1-t)."""
    y = np.asarray(y); p = np.asarray(p); n = len(y)
    out = np.empty(len(thresholds), dtype=float)
    for i, t in enumerate(thresholds):
        pred = p >= t
        tp = float(np.sum(pred & (y == 1)))
        fp = float(np.sum(pred & (y == 0)))
        out[i] = tp / n - fp / n * (t / (1.0 - t))
    return out


def mean_net_benefit(y: np.ndarray, p: np.ndarray,
                     t_lo: float = 0.05, t_hi: float = 0.5, n_thresholds: int = 19) -> float:
    """Mean decision-curve net benefit over a clinically-relevant threshold range (higher is
    better); summarises the area under the net-benefit curve. The reduced-vs-full difference is
    computed under the same threshold range, so the comparison is range-invariant."""
    ts = np.linspace(t_lo, t_hi, n_thresholds)
    return float(np.mean(net_benefit(y, p, ts)))


def conformal_covered(y: np.ndarray, p: np.ndarray, alpha: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """Split/cross-conformal binary prediction sets at nominal coverage 1-alpha.

    Nonconformity score of a label is ``1 - p_label``; the conformal threshold is the
    (1-alpha) empirical quantile of the true-label scores. Returns per-sample
    ``(covered, set_size)``. Marginal coverage is ~1-alpha by construction; the informative
    axes are set size (efficiency) and group-conditional coverage.
    """
    y = np.asarray(y); p = np.clip(np.asarray(p, dtype=float), 0.0, 1.0); p0 = 1.0 - p
    s_true = np.where(y == 1, 1.0 - p, 1.0 - p0)
    q = float(np.quantile(s_true, 1.0 - alpha, method="higher"))
    in1 = (1.0 - p) <= q
    in0 = (1.0 - p0) <= q
    set_size = in0.astype(int) + in1.astype(int)
    covered = np.where(y == 1, in1, in0).astype(bool)
    return covered, set_size


def conformal_efficiency(y: np.ndarray, p: np.ndarray, alpha: float = 0.1) -> float:
    """Mean conformal prediction-set size (lower is better; 2 = uninformative)."""
    _, ss = conformal_covered(y, p, alpha)
    return float(np.mean(ss))


def conformal_coverage(y: np.ndarray, p: np.ndarray, alpha: float = 0.1) -> float:
    """Realised marginal coverage of the conformal sets (~1-alpha by construction)."""
    cov, _ = conformal_covered(y, p, alpha)
    return float(np.mean(cov))


def selective_ece(y: np.ndarray, p: np.ndarray, coverage: float = 0.8, bins: int = 15) -> float:
    """ECE on the top-`coverage` most-confident predictions (calibration where the model is
    actually relied upon). Confidence is |p-0.5|."""
    y = np.asarray(y); p = np.asarray(p)
    conf = np.abs(p - 0.5)
    k = max(1, int(round(coverage * len(y))))
    idx = np.argsort(-conf, kind="mergesort")[:k]
    return expected_calibration_error(y[idx], p[idx], bins)


def operating_point(y: np.ndarray, p: np.ndarray, deferred: np.ndarray,
                    threshold: float = 0.5) -> dict:
    """Metrics at a model's *natural* abstention decision (boolean `deferred`).

    Retained = not deferred. Reports coverage and accuracy on the retained set,
    plus how many true positive cases the abstention routed away for review.
    """
    keep = ~deferred
    n = len(y)
    if keep.any():
        yhat = (p[keep] >= threshold).astype(int)
        acc = float((yhat == y[keep]).mean())
    else:
        acc = float("nan")
    deferred_at_risk = int((deferred & (y == 1)).sum())
    return {
        "natural_coverage": float(keep.mean()),
        "natural_selective_accuracy": acc,
        "deferred_fraction": float(deferred.mean()),
        "deferred_count": int(deferred.sum()),
        "deferred_at_risk_count": deferred_at_risk,
        "deferred_precision_at_risk": (
            deferred_at_risk / int(deferred.sum()) if deferred.sum() else float("nan")
        ),
    }
