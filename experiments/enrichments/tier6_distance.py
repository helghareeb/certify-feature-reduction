"""Tier 6 — distance-to-training-support confidence for AURC (review's the Tier 6 addendum).
Confidence = -d, where d = mean Euclidean distance from a held-out point to its m=10 nearest
neighbours in the SAME training fold, computed in the FULL feature space (X only, never the
classifier output), standardised on training-fold stats only. The SAME d is used for every budget,
so the reduced and full arms differ ONLY in the classifier's probability -- the clean test.

Modes:
  (default) sanity : 12 datasets, mutual_info, rep 0, FULL budget -> pooled + per-ds
                     Spearman(-d, |p-0.5|). p = RF mean-of-trees (mirrors Tier 4's convention).
                     |rho|<0.5 -> independent, proceed. 0.5..0.95 -> partial, report+proceed.
                     |rho|>=0.95 -> not independent, STOP (as Tier 4).
  --full           : AURC full-vs-aggressive penalty under conf=-d vs conf=|p-0.5|, main
                     12-dataset grid x 3 rankers x {rf,logistic}, reusing cached p_oof (no refit).
diabetes130 (~101k): BallTree (not brute force); if still slow, other 11 first then it.
Paired with Tier-1/Tier-4: same derive_seed, same StratifiedKFold folds.
"""
import sys, os, json, warnings, argparse
from pathlib import Path
if os.environ.get("XNSVAD_LOW_PRIORITY") == "1":  # BELOW_NORMAL so arcene/gli85 keep priority
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import BallTree
from scipy import stats
warnings.filterwarnings("ignore"); np.seterr(all="ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "src"))
from nsclinfs import data, reduction
from nsclinfs.seeds import derive_seed

REPO = Path(__file__).resolve().parents[0]
CFG = json.load(open(REPO / "config" / "calibration.json"))
MASTER = CFG["RANDOM_SEED"]; DATASETS = CFG["datasets"]; METHODS = CFG["reduction_methods"]; NFOLDS = CFG["n_folds"]
M_NN = 10  # nearest neighbours for distance-to-support
# diabetes130 must load the FULL cohort to match the cached p_oof (data.load default is a 6000 subsample)
_DS_PARAMS = CFG.get("dataset_params", {})


def _load(ds):
    X, y, s = data.load(ds, params=_DS_PARAMS.get(ds))
    X.attrs["name"] = ds
    return X, y, s


def aurc(y, p, conf):
    """Area under the risk-coverage curve; points ordered most-confident first (higher conf = kept)."""
    yhat = (p >= 0.5).astype(int); err = (yhat != y).astype(float)
    order = np.argsort(-conf, kind="mergesort")
    return float(np.trapezoid(np.cumsum(err[order]) / np.arange(1, len(y) + 1),
                              np.arange(1, len(y) + 1) / len(y)))


def oof_dist_and_p(X, y, method, rep):
    """Out-of-fold, paired CV. Returns (conf=-d in full space, p=RF mean-of-trees, mask)."""
    seed = derive_seed(MASTER, {"dataset": X.attrs.get("name"), "method": method, "classifier": "rf", "rep": rep})
    skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
    n = len(y)
    conf = np.full(n, np.nan); p = np.full(n, np.nan)
    for tr, te in skf.split(X, y):
        med = X.iloc[tr].median(numeric_only=True)
        Xtr_i, Xte_i = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
        # FULL feature space, standardised on training stats only (same leakage firewall).
        mu, sd = Xtr_i.mean(), Xtr_i.std(ddof=0).replace(0.0, 1.0)
        Xtr_z, Xte_z = ((Xtr_i - mu) / sd).to_numpy(), ((Xte_i - mu) / sd).to_numpy()
        # distance-to-training-support: mean Euclidean dist to m nearest TRAINING neighbours.
        tree = BallTree(Xtr_z, metric="euclidean")
        dist, _ = tree.query(Xte_z, k=M_NN)          # (n_te, m); held-out rows not in the tree
        conf[te] = -dist.mean(axis=1)                # nearer to support -> higher confidence
        # p for the sanity gate: RF mean-of-trees at FULL budget (mirrors Tier 4).
        rf = RandomForestClassifier(n_estimators=150, random_state=seed, n_jobs=1).fit(Xtr_z, y[tr])
        p[te] = rf.predict_proba(Xte_z)[:, 1]
    return conf, p, ~np.isnan(p)


ap = argparse.ArgumentParser(); ap.add_argument("--full", action="store_true")
ap.add_argument("--datasets", default="", help="comma list to run this invocation (default: all 12)")
a = ap.parse_args()
CACHE = REPO / "results" / "tier6_cache"; CACHE.mkdir(parents=True, exist_ok=True)

if not a.full:
    # SANITY: pooled + per-dataset Spearman(-d, |p-0.5|), mutual_info, rep 0, full budget.
    # Resumable & mergeable: each dataset's (conf, margin) points are cached to npz; the pooled
    # statistic is recomputed from EVERY cached dataset, so running 11 now + diabetes130 later
    # (option (a), after the calibrated addendum frees RAM) yields an exact pooled-over-12 result.
    run_list = [d.strip() for d in a.datasets.split(",") if d.strip()] or DATASETS
    for d in run_list:
        npz = CACHE / f"{d}.npz"
        if npz.exists():
            print(f"  {d:14s} cached, skip"); continue
        X, y, _ = _load(d)
        conf, p, ok = oof_dist_and_p(X, y, "mutual_info", 0)
        margin = np.abs(p[ok] - 0.5)
        np.savez(npz, conf=conf[ok], margin=margin, p=int(X.shape[1]))
        print(f"  {d:14s} n={int(ok.sum()):6d} p={X.shape[1]:6d}  "
              f"rho(-d,|p-.5|)={stats.spearmanr(conf[ok], margin).statistic:+.4f}  -> cached")
    # recompute pooled + per-dataset over ALL cached datasets present
    pooled_conf, pooled_margin, per_ds = [], [], {}
    for d in DATASETS:
        npz = CACHE / f"{d}.npz"
        if not npz.exists():
            continue
        z = np.load(npz); c, m = z["conf"], z["margin"]
        per_ds[d] = {"n": int(len(c)), "p": int(z["p"]), "rho": float(stats.spearmanr(c, m).statistic)}
        pooled_conf.append(c); pooled_margin.append(m)
    C, M = np.concatenate(pooled_conf), np.concatenate(pooled_margin)
    rho = float(stats.spearmanr(C, M).statistic)
    print(f"  [pooled over {len(per_ds)}/{len(DATASETS)} datasets present]")
    verdict = ("stop_not_independent" if abs(rho) >= 0.95 else
               "proceed_independent" if abs(rho) < 0.5 else "proceed_partial_independence")
    print(f"\n=== SANITY: pooled Spearman(-d, |p-0.5|) over {len(C)} points = {rho:+.5f} -> {verdict} ===")
    print("VERDICT:",
          ">=0.95 NOT independent -> report & STOP (as Tier 4)" if abs(rho) >= 0.95 else
          "<0.5 independent -> proceed to T6.3 measurement" if abs(rho) < 0.5 else
          "0.5..0.95 partial independence -> report the number & proceed to T6.3")
    json.dump({"pooled_spearman_negd_vs_margin": rho, "n_points": int(len(C)), "m_nn": M_NN,
               "verdict": verdict, "per_dataset": per_ds},
              open(REPO / "results" / "tier6_sanity.json", "w"), indent=2)
else:
    # T6.3 MEASUREMENT (sanity PASSED, rho=+0.21 independent): AURC full-vs-aggressive reduction penalty
    # under conf=-d vs conf=|p-0.5|, for the SAME cells. Reuses cached OOF p (calibrate=none) -> no refit.
    # -d is recomputed on the SAME folds as each cell (seed includes classifier, matching the cache).
    run_list = [d.strip() for d in a.datasets.split(",") if d.strip()] or DATASETS
    POOF = REPO / "results" / "cache" / "poof"
    FULL_B, AGGR_B = "frac:1", "frac:0.25"   # full vs most-aggressive fractional budget

    def oof_dist_only(X, y, method, clf, rep):
        """-d in FULL feature space, OOF, on the cell's own folds (no classifier fit)."""
        seed = derive_seed(MASTER, {"dataset": X.attrs.get("name"), "method": method,
                                    "classifier": clf, "rep": rep})
        skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
        conf = np.full(len(y), np.nan)
        for tr, te in skf.split(X, y):
            med = X.iloc[tr].median(numeric_only=True)
            Xtr, Xte = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
            mu, sd = Xtr.mean(), Xtr.std(ddof=0).replace(0.0, 1.0)
            tree = BallTree(((Xtr - mu) / sd).to_numpy(), metric="euclidean")
            dist, _ = tree.query(((Xte - mu) / sd).to_numpy(), k=M_NN)
            conf[te] = -dist.mean(axis=1)
        return conf

    rows = []
    for d in run_list:
        X, y, _ = _load(d)
        for method in METHODS:
            for clf in ["rf", "logistic"]:
                for rep in range(int(CFG["REPS"])):
                    f = POOF / f"{d}__{method}__{clf}__none__rep{rep}.parquet"
                    if not f.exists():
                        continue
                    pdf = pd.read_parquet(f)
                    if FULL_B not in pdf.columns or AGGR_B not in pdf.columns:
                        continue
                    yy = pdf["y"].to_numpy()
                    conf = oof_dist_only(X, yy, method, clf, rep)
                    ok = ~np.isnan(conf)
                    p1, pa = pdf[FULL_B].to_numpy(), pdf[AGGR_B].to_numpy()
                    # reduction penalty = AURC(aggressive) - AURC(full); positive = worse at aggr budget.
                    pen_margin = (aurc(yy[ok], pa[ok], np.abs(pa[ok] - 0.5))
                                  - aurc(yy[ok], p1[ok], np.abs(p1[ok] - 0.5)))
                    pen_d = aurc(yy[ok], pa[ok], conf[ok]) - aurc(yy[ok], p1[ok], conf[ok])
                    rows.append({"dataset": d, "method": method, "classifier": clf, "rep": rep,
                                 "penalty_margin": pen_margin, "penalty_d": pen_d})
        print(f"  {d}: cells so far = {len(rows)}")
    df = pd.DataFrame(rows)
    outcsv = REPO / "results" / f"tier6_measurement{'_' + a.datasets.split(',')[0] if a.datasets and len(run_list)==1 else ''}.csv"
    df.to_csv(outcsv, index=False)
    # aggregate: paired penalty_d vs penalty_margin across cells
    mm, md = df.penalty_margin.mean(), df.penalty_d.mean()
    ratio = md / mm if mm else float("nan")
    from scipy.stats import wilcoxon
    wil = wilcoxon(df.penalty_d)[1] if (df.penalty_d.abs() > 0).any() else float("nan")
    rho_pen = stats.spearmanr(df.penalty_margin, df.penalty_d).statistic
    verdict = ("persists" if md > 0 and ratio > 0.5 else
               "shrinks_materially" if md > 0 else "vanishes_or_reverses")
    summ = {"n_cells": len(df), "datasets": sorted(df.dataset.unique().tolist()),
            "mean_penalty_margin": float(mm), "mean_penalty_d": float(md),
            "survival_ratio_d_over_margin": float(ratio),
            "wilcoxon_p_penalty_d_ne_0": float(wil),
            "spearman_penalty_margin_vs_d": float(rho_pen), "verdict": verdict}
    json.dump(summ, open(REPO / "results" / "tier6_measurement_summary.json", "w"), indent=2)
    print("\n=== T6.3 MEASUREMENT ===")
    print(f"cells={len(df)}  mean penalty |p-.5|={mm:+.5f}  mean penalty -d={md:+.5f}  "
          f"survival={ratio:.2f}  wilcoxon(p_d!=0)={wil:.2e}  rho(margin,d)={rho_pen:+.3f}")
    print("VERDICT:", verdict,
          "-> selective reliability is INDEPENDENT evidence (penalty survives an X-only confidence)"
          if verdict == "persists" else
          "-> AURC degradation was substantially a probability-scale property (report at full prominence)")
