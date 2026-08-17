"""Tier 4 — ensemble-disagreement confidence for AURC (review's ADDENDUM + the Tier 4 plan).
Confidence = per-tree disagreement of the BASE random forest (std across estimators_ predict_proba),
which is NOT a function of the mean predicted probability. RF only, main 12-dataset grid, calibrate=none.

🔴 SANITY FIRST (the point of the exercise): pooled rank-correlation between the disagreement confidence
and |p-0.5|. If |rho| is near 1 the new confidence is not independent -> report and STOP before the grid.

Modes:
  (default) sanity : all 12 datasets, mutual_info, rep 0, FULL budget -> pooled Spearman(std, |p-0.5|).
  --full           : 12 datasets x 3 methods x 30 reps, full + aggressive(25%) budgets -> AURC penalty
                     under conf=|p-0.5| vs conf=-std; per-cell then aggregated. Writes tier4_*.csv.
Paired with Tier-1: same derive_seed, same folds, mean-of-trees == rf.predict_proba.
"""
import sys, json, warnings, argparse
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from scipy import stats
warnings.filterwarnings("ignore"); np.seterr(all="ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "src"))
from nsclinfs import data, reduction
from nsclinfs.seeds import derive_seed

REPO = Path(__file__).resolve().parents[0]
CFG = json.load(open(REPO / "config" / "calibration.json"))
MASTER = CFG["RANDOM_SEED"]; DATASETS = CFG["datasets"]; METHODS = CFG["reduction_methods"]; NFOLDS = CFG["n_folds"]

def aurc(y, p, conf):
    yhat = (p >= 0.5).astype(int); err = (yhat != y).astype(float)
    order = np.argsort(-conf, kind="mergesort")
    return float(np.trapezoid(np.cumsum(err[order]) / np.arange(1, len(y) + 1), np.arange(1, len(y) + 1) / len(y)))

def oof_mean_std(X, y, method, rep, ks):
    """Return {k: (mean_oof, std_oof)} — mean prob and per-tree std, out-of-fold, paired CV."""
    seed = derive_seed(MASTER, {"dataset": X.attrs.get("name"), "method": method, "classifier": "rf", "rep": rep})
    skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
    out = {k: (np.full(len(y), np.nan), np.full(len(y), np.nan)) for k in ks}
    for tr, te in skf.split(X, y):
        med = X.iloc[tr].median(numeric_only=True)
        Xtr_i, Xte_i = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
        ranking = reduction.rank(method, Xtr_i, y[tr], seed)
        for k in ks:
            feats = ranking[:k]
            mu, sd = Xtr_i[feats].mean(), Xtr_i[feats].std(ddof=0).replace(0.0, 1.0)
            Xtr_z, Xte_z = (Xtr_i[feats] - mu) / sd, (Xte_i[feats] - mu) / sd
            rf = RandomForestClassifier(n_estimators=150, random_state=seed, n_jobs=1).fit(Xtr_z, y[tr])
            per_tree = np.stack([t.predict_proba(Xte_z)[:, 1] for t in rf.estimators_])  # (150, n_te)
            out[k][0][te] = per_tree.mean(0)
            out[k][1][te] = per_tree.std(0)
    return out

ap = argparse.ArgumentParser(); ap.add_argument("--full", action="store_true"); a = ap.parse_args()

if not a.full:
    # SANITY: pooled Spearman(std, |p-0.5|) at full budget, mutual_info, rep 0
    pooled_std, pooled_margin = [], []
    for d in DATASETS:
        X, y, _ = data.load(d); X.attrs["name"] = d
        p = X.shape[1]; res = oof_mean_std(X, y, "mutual_info", 0, [p])
        mean, std = res[p]; ok = ~np.isnan(mean)
        pooled_std.append(std[ok]); pooled_margin.append(np.abs(mean[ok] - 0.5))
        print(f"  {d:14s} n={len(y):6d} p={p:6d}  local rho(std,|p-.5|)={stats.spearmanr(std[ok], np.abs(mean[ok]-0.5)).statistic:+.4f}")
    S, M = np.concatenate(pooled_std), np.concatenate(pooled_margin)
    rho = stats.spearmanr(S, M).statistic
    print(f"\n=== SANITY: pooled Spearman(disagreement std, |p-0.5|) over {len(S)} points = {rho:+.5f} ===")
    print("VERDICT:", "NEAR +-1 -> disagreement NOT independent of |p-0.5| -> report & STOP (arm cannot answer)"
          if abs(rho) >= 0.95 else "not near +-1 -> disagreement is a genuinely independent confidence -> proceed to --full")
    json.dump({"pooled_spearman_std_vs_margin": rho, "n_points": int(len(S)), "verdict":
               "stop_not_independent" if abs(rho) >= 0.95 else "proceed"},
              open(REPO / "results" / "tier4_sanity.json", "w"), indent=2)
else:
    print("FULL Tier-4 run (AURC penalty under disagreement vs |p-0.5|) — placeholder gated on sanity PASS.")
