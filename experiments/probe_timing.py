"""Timing probe for the full-cohort Diabetes-130 grid (Stage 1 of the revision).

Measures, on ONE stratified 5-fold split (fold 0, ~81k train rows), the atomic costs the
grid formula needs:
  - each ranking method (mutual_info, rf_importance, l1) on the full training fold
  - each classifier fit+predict at k=16 (full) and k=4 (reduced)
  - rf + isotonic and rf + sigmoid calibrated fits (the suspected cliff)
  - peak RSS of the largest RF fit (memory gate for multi-process parallelism)

Output: results/timing_probe.json — informational, NOT hash-gated, never read by the
aggregator. Projection math lives in the revision notes; this script only measures.

    PYTHONPATH=src python experiments/probe_timing.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def rss_mb() -> float:
    try:
        import psutil  # type: ignore
        return psutil.Process().memory_info().rss / 1e6
    except Exception:
        import ctypes
        import ctypes.wintypes as wt

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = PMC(cb=ctypes.sizeof(PMC))
        ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),
                                                 ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize / 1e6


def main() -> None:
    from sklearn.model_selection import StratifiedKFold

    from nsclinfs import data as dataload
    from nsclinfs import reduction
    from nsclinfs.run import _fit_predict

    t0 = time.perf_counter()
    X, y, sens = dataload.load("diabetes130", params={"n_target": None})
    load_s = time.perf_counter() - t0
    n, p = X.shape
    print(f"full cohort: n={n} p={p} prevalence={y.mean():.4f} (loaded in {load_s:.1f}s)")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    tr, te = next(iter(skf.split(X, y)))
    # mirror _eval_fracs preprocessing exactly: per-fold median impute, per-subset z-score
    med = X.iloc[tr].median(numeric_only=True)
    Xtr_i, Xte_i = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
    ytr = y[tr]
    print(f"fold 0: train={len(tr)} test={len(te)}")

    out: dict = {"n_full": int(n), "p": int(p), "prevalence": float(y.mean()),
                 "train_rows": int(len(tr)), "loader_s": round(load_s, 2), "rankings_s": {},
                 "fit_s": {}, "calibrated_fit_s": {}, "peak_rss_mb": None}

    ranking = None
    for method in ("mutual_info", "rf_importance", "l1_logistic"):
        t = time.perf_counter()
        ranking = reduction.rank(method, Xtr_i, ytr, 12345)
        out["rankings_s"][method] = round(time.perf_counter() - t, 2)
        print(f"ranking {method:14s} {out['rankings_s'][method]:8.2f}s")

    def z(df, feats):
        mu, sd = Xtr_i[feats].mean(), Xtr_i[feats].std(ddof=0).replace(0.0, 1.0)
        return (df[feats] - mu) / sd

    for clf in ("logistic", "rf", "gb"):
        for k in (p, 4):
            feats = ranking[:k]
            t = time.perf_counter()
            _fit_predict(clf, "none", z(Xtr_i, feats), ytr, z(Xte_i, feats), 12345)
            out["fit_s"][f"{clf}_k{k}"] = round(time.perf_counter() - t, 2)
            print(f"fit {clf:8s} k={k:<3d} {out['fit_s'][f'{clf}_k{k}']:8.2f}s")

    for cal in ("isotonic", "sigmoid"):
        t = time.perf_counter()
        _fit_predict("rf", cal, z(Xtr_i, ranking), ytr, z(Xte_i, ranking), 12345)
        out["calibrated_fit_s"][f"rf_{cal}"] = round(time.perf_counter() - t, 2)
        print(f"fit rf+{cal:8s} k={p:<3d} {out['calibrated_fit_s'][f'rf_{cal}']:8.2f}s")

    out["peak_rss_mb"] = round(rss_mb(), 1)
    print(f"peak RSS {out['peak_rss_mb']:.0f} MB")
    dest = ROOT / "results" / "timing_probe.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
