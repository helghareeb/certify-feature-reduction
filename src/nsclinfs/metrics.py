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


def equal_width_bin_index(p: np.ndarray, bins: int = 15) -> np.ndarray:
    """Bin assignment for equal-width calibration bins over [0, 1].

    Factored out so the calibration-error and the reliability/resolution decompositions below
    partition the predictions identically; a decomposition binned differently from the error it
    decomposes is not a decomposition of it.
    """
    edges = np.linspace(0.0, 1.0, bins + 1)
    return np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)


def expected_calibration_error(y: np.ndarray, p: np.ndarray, bins: int = 15) -> float:
    idx = equal_width_bin_index(p, bins)
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


def murphy_decomposition(y: np.ndarray, p: np.ndarray, bins: int = 15) -> dict:
    """Murphy's decomposition of the Brier score: reliability - resolution + uncertainty.

    Reliability is calibration error (lower is better) and is what ECE measures. **Resolution is
    how far the binned outcome rates depart from the base rate -- how much the model discriminates
    at all -- and ECE has no such term.** A model that predicts the base rate for every patient has
    zero reliability error and zero resolution: perfectly calibrated, perfectly uninformative. Under
    an aggressive feature budget that is a reachable state, so a falling calibration error can mean
    either a better-calibrated model or a collapsed one, and the two are told apart by resolution.

    `n_occupied` and `largest_bin_share` are reported beside the terms because a decomposition over
    one occupied bin is arithmetic rather than evidence.

    The identity is exact for a forecast taking one value per bin, so it is stated against
    `brier_binned` -- the Brier score of the bin-mean forecast, which is the object ECE also scores.
    `binning_residual` is what the binning discards, ``brier - brier_binned``; it is reported rather
    than hidden so the decomposition can be checked against the Brier score the study actually
    reports. `tests/test_metrics_closed_form.py` asserts both.
    """
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    n = len(y)
    ybar = float(y.mean())
    idx = equal_width_bin_index(p, bins)
    reliability = resolution = 0.0
    occupied = 0
    largest = 0
    for b in range(bins):
        m = idx == b
        nk = int(m.sum())
        if nk == 0:
            continue
        occupied += 1
        largest = max(largest, nk)
        reliability += nk * (p[m].mean() - y[m].mean()) ** 2
        resolution += nk * (y[m].mean() - ybar) ** 2
    reliability /= n
    resolution /= n
    uncertainty = ybar * (1.0 - ybar)
    brier_binned = reliability - resolution + uncertainty
    brier = float(np.mean((p - y) ** 2))
    return {
        "reliability": float(reliability),
        "resolution": float(resolution),
        "uncertainty": float(uncertainty),
        "brier_binned": float(brier_binned),
        "brier": brier,
        "binning_residual": float(brier - brier_binned),
        "n_occupied": occupied,
        "largest_bin_share": float(largest / n),
        "n_distinct": int(len(np.unique(np.round(p, 9)))),
        "sd_p": float(p.std()),
    }


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

    The sort is **stable**, so equally-confident samples are retained in the order they appear in
    the dataset. That is immaterial when confidences are near-distinct, as they are at generous
    feature budgets, and material at the most aggressive ones, where a one-feature model emits few
    distinct scores and tie blocks are large: `results/enrichments/20_metric_diagnostics` measures
    how far AURC moves under row permutation. Stability is kept deliberately -- it makes the number
    reproducible, and the alternative of randomising ties would move every published AURC -- but the
    permutation range is reported in the manuscript's threats section rather than left implicit.
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


def net_benefit_treat_all(prevalence: float, thresholds: np.ndarray) -> np.ndarray:
    """Net benefit of the default strategy that treats every patient.

    Treating everyone makes TP/n the prevalence and FP/n its complement, so
    ``NB_all(t) = prev - (1 - prev) * t/(1 - t)``. A decision curve is only interpretable against
    the default strategies, and this is the one that binds at high prevalence: when the evaluated
    threshold range lies below the prevalence, treat-all is strong there and a model has to beat it
    to be worth anything.
    """
    t = np.asarray(thresholds, dtype=float)
    return prevalence - (1.0 - prevalence) * t / (1.0 - t)


def mean_net_benefit_treat_all(prevalence: float, t_lo: float = 0.05, t_hi: float = 0.5,
                               n_thresholds: int = 19) -> float:
    """`mean_net_benefit`'s treat-all counterpart, over the identical threshold grid."""
    ts = np.linspace(t_lo, t_hi, n_thresholds)
    return float(np.mean(net_benefit_treat_all(prevalence, ts)))


def conformal_covered(y: np.ndarray, p: np.ndarray, alpha: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """**Transductive** (full-sample) conformal binary prediction sets at nominal coverage 1-alpha.

    Nonconformity score of a label is ``1 - p_label``; the conformal threshold is the
    (1-alpha) empirical quantile of the true-label scores. Returns per-sample
    ``(covered, set_size)``.

    Note what guarantees coverage here. The quantile is taken over the same points the sets are
    then evaluated on, so ``coverage >= 1-alpha`` follows from the definition of the empirical
    quantile and needs no exchangeability argument -- this is *not* split conformal, where the
    quantile comes from a held-out calibration set and exchangeability is what does the work.
    `results/enrichments/20_metric_diagnostics` measures the difference against a textbook split:
    at most 0.017 in mean set size, and in the conservative direction. The informative axes are
    set size (efficiency) and group-conditional coverage, and both comparisons in this study are
    made between arms that use this same estimator.
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
