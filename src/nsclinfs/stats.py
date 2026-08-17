"""Paired statistics for the audit: Holm step-down (R3) and percentile bootstrap (R12).

Outcomes are paired across repetitions: at a given (dataset, ranker, learner) the same
per-repetition cross-validation split is shared by every reduction level, so each reduced
model is paired against its own full-feature baseline on identical folds. We therefore use the
Wilcoxon signed-rank test, paired Cohen's d, and a paired-difference percentile bootstrap.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

BOOTSTRAP_DEFAULT: int = 5000


def paired_wilcoxon(a: np.ndarray, b: np.ndarray) -> float:
    """Two-sided Wilcoxon signed-rank p-value for paired samples a, b."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = a - b
    if d.size == 0 or np.allclose(d, 0.0):
        return 1.0
    try:
        return float(wilcoxon(a, b, zero_method="wilcox", alternative="two-sided").pvalue)
    except ValueError:
        return 1.0


def holm(pvalues: list[float]) -> np.ndarray:
    """Holm step-down corrected p-values. p_holm >= p_raw by construction (R3)."""
    if len(pvalues) == 0:
        return np.array([])
    return multipletests(pvalues, method="holm")[1]


def benjamini_hochberg(pvalues: list[float], alpha: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg FDR-adjusted p-values (less conservative than Holm).

    Used ONLY for the SUPPLEMENTARY global-multiplicity robustness check (Rec 8):
    the pre-registered gate corrects Holm *within* each (scenario, outcome) family;
    this controls the FDR *across* all tests at once. It never replaces the frozen
    Holm gate.
    """
    if len(pvalues) == 0:
        return np.array([])
    return multipletests(pvalues, alpha=alpha, method="fdr_bh")[1]


def cohens_d_paired(a: np.ndarray, b: np.ndarray) -> float:
    """Paired Cohen's d = mean(diff) / sd(diff)."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    if d.size < 2:
        return 0.0
    sd = d.std(ddof=1)
    return float(d.mean() / sd) if sd > 0 else 0.0


def bootstrap_diff_ci(
    a: np.ndarray,
    b: np.ndarray,
    n_resamples: int = BOOTSTRAP_DEFAULT,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the paired mean difference mean(a - b) (R12)."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    n = d.size
    if n == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    means = d[idx].mean(axis=1)
    lo = float(np.percentile(means, 100 * alpha / 2))
    hi = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return (lo, hi)


def mean_ci(
    values: np.ndarray,
    n_resamples: int = BOOTSTRAP_DEFAULT,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Percentile bootstrap CI for a single-sample mean (R12)."""
    v = np.asarray(values, dtype=float)
    n = v.size
    if n == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    means = v[idx].mean(axis=1)
    lo = float(np.percentile(means, 100 * alpha / 2))
    hi = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return (lo, hi)
