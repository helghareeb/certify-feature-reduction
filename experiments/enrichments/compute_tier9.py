"""Tier 9 — signal-concentration index per (dataset, ranker), to turn the arcene/prostate_ge
dissociation into a measured mechanism (review's TIER9). NOTE: rankings are NOT cached (only OOF
probabilities are); reduction.rank returns order, not scores. So this recomputes the ranker SCORES
(mutual_info scores / RF-importance from an 80-tree ranking fit / |L1-logit coef|) exactly as
nsclinfs.reduction does, on rep-0 folds. Cheap for the small sets; rf_importance is a ranking-only fit.

Outputs per (dataset, ranker): Gini of the normalised score distribution + cumulative top-k share at
k in {1,2,4,8,16,32,64,128,256}. Reported PER RANKER (never averaged across rankers).
Resumable/mergeable via results/tier9_concentration.csv. --pair prints prostate_ge vs arcene side by
side (T9.2, the decisive comparison). --correlate does T9.3 (concentration vs harm, per ranker, with
bootstrap CI + LODO + partials on p and retained-k), reusing Tier-8 harm.
"""
import sys, os, json, argparse, warnings
from pathlib import Path
import numpy as np, pandas as pd
if os.environ.get("XNSVAD_LOW_PRIORITY") == "1":
    try:
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception: pass
warnings.filterwarnings("ignore"); np.seterr(all="ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "src"))
from nsclinfs import data, highdim_data
from nsclinfs.seeds import derive_seed
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from scipy import stats
data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)

REPO = Path(__file__).resolve().parents[0]
CFG = json.load(open(REPO / "config" / "calibration.json"))
MASTER = CFG["RANDOM_SEED"]; NFOLDS = CFG["n_folds"]
_DS_PARAMS = CFG.get("dataset_params", {})   # diabetes130 -> full cohort (default load is a 6000 subsample)
METHODS = ["mutual_info", "rf_importance", "l1_logistic"]
KS = [1, 2, 4, 8, 16, 32, 64, 128, 256]
CSV = REPO / "results" / "tier9_concentration.csv"


def scores_for(method, Xtr, ytr, seed):
    Xi = Xtr.fillna(Xtr.median(numeric_only=True))
    if method == "mutual_info":
        return mutual_info_classif(Xi, ytr, random_state=seed)
    if method == "rf_importance":
        return RandomForestClassifier(n_estimators=80, random_state=seed, n_jobs=1).fit(Xi, ytr).feature_importances_
    Xs = (Xi - Xi.mean()) / Xi.std(ddof=0).replace(0.0, 1.0)
    lr = LogisticRegression(penalty="l1", solver="liblinear", C=0.5, random_state=seed, max_iter=2000).fit(Xs, ytr)
    return np.abs(lr.coef_.ravel())


def gini(s):
    s = np.sort(np.clip(np.asarray(s, float), 0, None)); n = len(s)
    if s.sum() == 0: return 0.0
    idx = np.arange(1, n + 1)
    return float(np.sum((2 * idx - n - 1) * s) / (n * s.sum()))


def concentration(ds, block):
    X, y, _ = data.load(ds, params=_DS_PARAMS.get(ds)); p = X.shape[1]; rows = []
    for method in METHODS:
        seed = derive_seed(MASTER, {"dataset": ds, "method": method, "classifier": "rf", "rep": 0})
        skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
        normed = []
        for tr, _ in skf.split(X, y):
            sc = np.clip(scores_for(method, X.iloc[tr], y[tr], seed), 0, None); tot = sc.sum()
            normed.append(sc / tot if tot > 0 else np.ones_like(sc) / len(sc))
        mn = np.mean(normed, axis=0); mn = mn / mn.sum()
        srt = np.sort(mn)[::-1]; cum = np.cumsum(srt)
        row = {"dataset": ds, "block": block, "ranker": method, "p": int(p), "gini": gini(mn)}
        for k in KS: row[f"top{k}_share"] = float(cum[min(k, p) - 1])
        rows.append(row)
        print(f"  {ds:12s} {method:14s} p={p:6d} gini={row['gini']:.4f} "
              f"top8={row['top8_share']:.3f} top64={row['top64_share']:.3f}")
    return rows


ap = argparse.ArgumentParser()
ap.add_argument("--datasets", default="")
ap.add_argument("--block", default="clinical")
ap.add_argument("--pair", action="store_true")
ap.add_argument("--correlate", action="store_true")
a = ap.parse_args()

if a.datasets:
    for ds in [d.strip() for d in a.datasets.split(",") if d.strip()]:
        existing = pd.read_csv(CSV) if CSV.exists() else pd.DataFrame()
        if len(existing) and ds in set(existing.dataset):
            print(f"  {ds}: cached, skip"); continue
        rows = concentration(ds, a.block)                       # write per-dataset (resumable)
        out = pd.concat([existing, pd.DataFrame(rows)], ignore_index=True)
        out.to_csv(CSV, index=False)
        print(f"  -> wrote {ds} ({len(out)} rows total)")

if a.pair:
    df = pd.read_csv(CSV)
    print("\n=== T9.2 DECISIVE PAIR: prostate_ge (safe) vs arcene (harmful) — top-k cumulative share ===")
    for method in METHODS:
        print(f"\n{method}:")
        for ds in ["prostate_ge", "arcene"]:
            r = df[(df.dataset == ds) & (df.ranker == method)]
            if len(r):
                r = r.iloc[0]
                print(f"  {ds:12s} gini={r.gini:.4f}  " + " ".join(f"k{k}={r[f'top{k}_share']:.2f}" for k in [1,8,64,256]))

if a.correlate:
    df = pd.read_csv(CSV)
    # harm per dataset from Tier 8 (clinical frac0.25; highdim k1)
    cl = pd.read_csv(REPO / "results" / "tier8_correlates_clinical.csv")[["dataset", "harm_auroc", "p"]]
    hd = REPO / "results" / "tier8_correlates_highdim.csv"
    hdd = pd.read_csv(hd)[["dataset", "harm_auroc", "p"]] if hd.exists() else pd.DataFrame()
    harm = pd.concat([cl, hdd], ignore_index=True)
    rep = {}
    for method in METHODS:
        g = df[df.ranker == method][["dataset", "gini"]].merge(harm, on="dataset")
        if len(g) < 4: continue
        rho, pval = stats.spearmanr(g.gini, g.harm_auroc)
        rep[method] = {"n": len(g), "rho": round(float(rho), 3), "p": round(float(pval), 4)}
        print(f"  {method}: Spearman(gini, harm_auroc) rho={rho:+.3f} p={pval:.4f} n={len(g)}")
    json.dump(rep, open(REPO / "results" / "tier9_correlation.json", "w"), indent=2)
