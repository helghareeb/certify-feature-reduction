"""Leakage-safe experiment: feature ranking + scaling + classifier fit INSIDE each CV
fold; out-of-fold probabilities pooled and scored once per (frac) cell.

The expensive feature ranking is computed once per (method, classifier, rep, fold) and
sliced to the top-k for each reduction level -- exact and ~5x faster than refitting the
selector per level. A cell = (dataset, method, classifier, frac, rep); `frac` (fraction
of features kept) is the independent variable.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from . import reduction
from .fairness import auroc_gap, conformal_coverage_gap, ece_gap, net_benefit_gap
from .metrics import (
    aurc,
    conformal_coverage,
    conformal_efficiency,
    mean_net_benefit,
    net_benefit,
    predictive_metrics,
    selective_ece,
)
from .seeds import derive_seed


def _classifier(name: str, seed: int):
    if name == "logistic":
        return LogisticRegression(max_iter=2000, random_state=seed)
    if name == "rf":
        return RandomForestClassifier(n_estimators=150, random_state=seed, n_jobs=1)
    if name == "gb":
        return HistGradientBoostingClassifier(random_state=seed)
    raise ValueError(name)


def _fit_predict(classifier: str, calibrate: str, Xtr, ytr, Xte, seed: int) -> np.ndarray:
    """Fit the base learner (calibrate='none') or a leakage-safe post-hoc recalibration of it
    (Platt 'sigmoid' / 'isotonic') using an INNER cross-validation of the training fold only --
    the calibrator never sees the outer held-out fold -- and return positive-class probabilities."""
    base = _classifier(classifier, seed)
    if calibrate == "none":
        model = base.fit(Xtr, ytr)
    else:
        model = CalibratedClassifierCV(base, method=calibrate, cv=3).fit(Xtr, ytr)
    return model.predict_proba(Xte)[:, 1]


def _eval_budgets(X, y, sensitive, *, method, classifier, seed, budgets, n_folds,
                  calibrate="none", collect_p_oof=None, collect_nb=None,
                  metric_params=None) -> list[dict]:
    """Evaluate a list of budget levels. Each level is ("frac", f) or ("k", k).

    All levels share the same folds and the same full per-fold rankings (computed once),
    so every level is paired with every other and with the full-feature reference. Distinct
    retained-k values are computed once and emitted under every level that maps to them —
    a k-level equal to a frac-derived k is bitwise the same model, at zero extra cost.

    `collect_p_oof`, when a dict, receives {level_label: p_oof array} for the caller to
    persist (the R1.3 worked-example cache); it does not change any metric.
    """
    n_features = X.shape[1]
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    folds = []
    for tr, te in skf.split(X, y):
        med = X.iloc[tr].median(numeric_only=True)
        Xtr_i, Xte_i = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
        ranking = reduction.rank(method, Xtr_i, y[tr], seed)   # full order, once per fold
        folds.append((tr, te, Xtr_i, Xte_i, ranking))

    levels = []                       # (budget_type, budget_value, label, k)
    for btype, bval in budgets:
        if btype == "frac":
            k = reduction.retained_k(float(bval), n_features)
        else:
            k = int(bval)
            if k >= n_features:       # k >= p is just the full model; skip except via frac 1.0
                continue
        levels.append((btype, bval, f"{btype}:{bval:g}", k))

    p_oof_by_k: dict[int, np.ndarray] = {}
    for k in sorted({k for *_, k in levels}, reverse=True):
        p_oof = np.full(len(y), np.nan)
        for tr, te, Xtr_i, Xte_i, ranking in folds:
            feats = ranking[:k]
            mu, sd = Xtr_i[feats].mean(), Xtr_i[feats].std(ddof=0).replace(0.0, 1.0)
            p_oof[te] = _fit_predict(classifier, calibrate, (Xtr_i[feats] - mu) / sd, y[tr],
                                     (Xte_i[feats] - mu) / sd, seed)
        p_oof_by_k[k] = p_oof

    mp = metric_params or {}
    nb = mp.get("net_benefit", {})
    nb_args = (float(nb.get("t_lo", 0.05)), float(nb.get("t_hi", 0.5)), int(nb.get("n_thresholds", 19)))
    curve = mp.get("nb_curve_grid", {})
    ts_curve = np.linspace(float(curve.get("t_lo", 0.01)), float(curve.get("t_hi", 0.5)),
                           int(curve.get("n", 50)))

    rows = []
    for btype, bval, label, k in levels:
        p_oof = p_oof_by_k[k]
        if collect_p_oof is not None:
            collect_p_oof[label] = p_oof
        if collect_nb is not None:
            collect_nb[label] = (ts_curve, net_benefit(y, p_oof, ts_curve))
        pm = predictive_metrics(y, p_oof)
        rows.append({
            "method": method, "budget_type": btype, "budget": label,
            "frac": float(bval) if btype == "frac" else np.nan,
            "k_features": k, "n_features": n_features,
            "classifier": classifier, "calibrate": calibrate, "seed": int(seed),
            "accuracy": pm["accuracy"], "auroc": pm["auroc"], "brier": pm["brier"], "ece": pm["ece"],
            "aurc": aurc(y, p_oof, np.abs(p_oof - 0.5)),
            "auroc_gap": auroc_gap(y, p_oof, sensitive), "ece_gap": ece_gap(y, p_oof, sensitive),
            # new reliability axes (all from the same out-of-fold probabilities)
            "net_benefit": mean_net_benefit(y, p_oof, *nb_args),
            "net_benefit_gap": net_benefit_gap(y, p_oof, sensitive),
            "conformal_efficiency": conformal_efficiency(y, p_oof),
            "conformal_coverage": conformal_coverage(y, p_oof),
            "conformal_coverage_gap": conformal_coverage_gap(y, p_oof, sensitive),
            "selective_ece": selective_ece(y, p_oof),
        })
    return rows


def _eval_fracs(X, y, sensitive, *, method, classifier, seed, fracs, n_folds, calibrate="none") -> list[dict]:
    """v1-compatible wrapper: fractional budgets only. Kept for run_cell and the tests."""
    return _eval_budgets(X, y, sensitive, method=method, classifier=classifier, seed=seed,
                         budgets=[("frac", f) for f in fracs], n_folds=n_folds, calibrate=calibrate)


def run_cell(X, y, sensitive, *, frac, method, classifier, seed, n_folds=5, calibrate="none") -> dict:
    return _eval_fracs(X, y, sensitive, method=method, classifier=classifier,
                       seed=seed, fracs=[frac], n_folds=n_folds, calibrate=calibrate)[0]


def run_grid(X, y, sensitive, *, fracs=None, budgets=None, methods, classifiers, n_reps,
             master_seed, n_folds=5, dataset="cleveland", rep_start=0, rep_end=None,
             calibrations=("none",), metric_params=None, persist=None) -> pd.DataFrame:
    """Run the grid. Budgets come either as `fracs` (v1 form) or `budgets`
    (v2: {"fracs": [...], "ks": [...]}). `persist`, when given, is
    {"p_oof_cells": [ {dataset,method,classifier,calibrate}, ... ], "dir": path,
     "nb_curves": bool} — matching cells get their per-rep out-of-fold probabilities
    written as parquet, and (when nb_curves) every cell's per-threshold net-benefit
    curve is collected onto the returned frame's attrs["nb_curves"] rows.
    """
    if budgets is not None:
        levels = ([("frac", float(f)) for f in budgets.get("fracs", [])]
                  + [("k", int(k)) for k in budgets.get("ks", [])])
    else:
        levels = [("frac", float(f)) for f in fracs]
    rep_end = n_reps if rep_end is None else rep_end
    p_cfg = persist or {}
    poof_cells = [tuple(sorted(c.items())) for c in p_cfg.get("p_oof_cells", [])]
    nb_rows: list[dict] = []
    rows = []
    for method in methods:
        for classifier in classifiers:
            for calibrate in calibrations:
                cell_id = {"dataset": dataset, "method": method,
                           "classifier": classifier, "calibrate": calibrate}
                want_poof = tuple(sorted(cell_id.items())) in poof_cells
                for rep in range(rep_start, rep_end):
                    # seed independent of budget/calibrate -> reduction levels (and raw vs
                    # recalibrated) share the CV split, so every comparison is paired.
                    seed = derive_seed(master_seed, {"dataset": dataset, "method": method,
                                                     "classifier": classifier, "rep": rep})
                    t_rep = time.perf_counter()
                    poof: dict | None = {} if want_poof else None
                    nbc: dict | None = {} if p_cfg.get("nb_curves") else None
                    rep_rows = _eval_budgets(X, y, sensitive, method=method, classifier=classifier,
                                             seed=seed, budgets=levels, n_folds=n_folds,
                                             calibrate=calibrate, collect_p_oof=poof,
                                             collect_nb=nbc, metric_params=metric_params)
                    runtime_s = time.perf_counter() - t_rep
                    for r in rep_rows:
                        r["dataset"] = dataset
                        r["rep"] = rep
                        r["runtime_s"] = round(runtime_s / len(rep_rows), 3)
                        rows.append(r)
                    if poof:
                        _write_poof(p_cfg.get("dir", "results/cache/poof"), cell_id, rep, y,
                                    sensitive, poof)
                    if nbc:
                        for label, (ts, vals) in nbc.items():
                            nb_rows += [{**cell_id, "rep": rep, "budget": label,
                                         "t": float(t), "nb": float(v)} for t, v in zip(ts, vals)]
    out = pd.DataFrame(rows)
    out.attrs["nb_curves"] = nb_rows
    return out


def _write_poof(base_dir, cell_id: dict, rep: int, y, sensitive, poof: dict) -> None:
    """Persist one rep's out-of-fold probabilities for a configured cell (R1.3 cache).
    One parquet per (cell, rep): row index, y, sensitive, one float32 column per budget."""
    from pathlib import Path
    d = Path(base_dir)
    d.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"y": np.asarray(y, dtype=np.int8),
                       "sensitive": pd.Series(sensitive).astype(str)})
    for label, p in poof.items():
        df[label] = np.asarray(p, dtype=np.float32)
    name = "__".join(str(cell_id[k]) for k in ("dataset", "method", "classifier", "calibrate"))
    df.to_parquet(d / f"{name}__rep{rep}.parquet", index=True)
