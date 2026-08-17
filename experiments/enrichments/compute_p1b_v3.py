"""P1 Arm B v3 -- LEAKAGE-FREE (agent's finding the Arm B leakage finding).
v2 selected the kept set by ranking the whole dataset (incl. labels) ONCE outside CV -> the reduced-25
model at small keep drew from a label-optimised pool (optimistic bias that grows as keep shrinks, i.e.
exactly the measured direction). Fix: select the kept POOL inside each training fold (train labels only),
then rank within the pool and reduce to fixed k=25. keep=10000 is the anchor (pool = all features either
way; must reproduce v2's +0.0914 -> harness sound, only biased rows move). Arm A unaffected, unchanged.
30 reps x 3 rankers x {logistic,rf}, fixed k=25, per-unit rows + bootstrap CI. Frozen code untouched.
"""
import sys, os, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
if os.environ.get("XNSVAD_LOW_PRIORITY") == "1":
    try:
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception: pass
warnings.filterwarnings("ignore"); np.seterr(all="ignore")
REPO = Path(__file__).resolve().parents[0]; sys.path.insert(0, str(REPO / "src"))
from nsclinfs import data, reduction, highdim_data
from nsclinfs.seeds import derive_seed
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)
MASTER, NFOLDS, REPS, KFIX = 20260626, 5, 30, 25
METHODS = ["mutual_info", "rf_importance", "l1_logistic"]; CLFS = ["logistic", "rf"]
KEEPS = [100, 256, 1000, 5000, 10000]


def aurc(y, p, conf):
    yhat = (p >= 0.5).astype(int); err = (yhat != y).astype(float)
    order = np.argsort(-conf, kind="mergesort")
    return float(np.trapezoid(np.cumsum(err[order]) / np.arange(1, len(y) + 1), np.arange(1, len(y) + 1) / len(y)))


def clf(name, seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    return LogisticRegression(max_iter=2000, random_state=seed) if name == "logistic" \
        else RandomForestClassifier(n_estimators=150, random_state=seed, n_jobs=1)


def cell(X, y, keep, method, cname, rep):
    seed = derive_seed(MASTER, {"dataset": "arcene", "method": method, "classifier": cname, "rep": rep,
                                "keep": keep})
    skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
    n = len(y); pf, pr = np.full(n, np.nan), np.full(n, np.nan)
    for tr, te in skf.split(X, y):
        med = X.iloc[tr].median(numeric_only=True)
        Xtr, Xte = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
        pool = reduction.rank("rf_importance", Xtr, y[tr], seed)[:keep]      # kept set, IN-FOLD (train labels only)
        ranking = reduction.rank(method, Xtr[pool], y[tr], seed)            # rank within the pool
        for feats, dst in ((pool, pf), (ranking[:KFIX], pr)):
            mu, sd = Xtr[feats].mean(), Xtr[feats].std(ddof=0).replace(0.0, 1.0)
            m = clf(cname, seed).fit((Xtr[feats] - mu) / sd, y[tr])
            dst[te] = m.predict_proba((Xte[feats] - mu) / sd)[:, 1]
    ok = ~np.isnan(pf) & ~np.isnan(pr)
    return roc_auc_score(y[ok], pf[ok]), roc_auc_score(y[ok], pr[ok])


X, y, _ = data.load("arcene"); X.attrs["name"] = "arcene"; y = np.asarray(y)
rows = []
for keep in KEEPS:
    for method in METHODS:
        for cname in CLFS:
            for rep in range(REPS):
                af, ar = cell(X, y, keep, method, cname, rep)
                rows.append(dict(kept_features=keep, method=method, classifier=cname, rep=rep,
                                 auroc_full=af, auroc_red=ar, auroc_penalty=af - ar))
    g = pd.DataFrame([r for r in rows if r["kept_features"] == keep])
    print(f"  keep {keep:5d}: full={g.auroc_full.mean():.4f} red25={g.auroc_red.mean():.4f} "
          f"penalty={g.auroc_penalty.mean():+.4f} (sd {g.auroc_penalty.std():.4f})")
d = pd.DataFrame(rows); d.to_csv(REPO / "results" / "p1_arcene_reverse_v3_rows.csv", index=False)


def ci(v, seed=20260626, B=2000):
    v = np.asarray(v, float); rng = np.random.RandomState(seed)
    bs = [v[rng.randint(0, len(v), len(v))].mean() for _ in range(B)]
    return round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)


agg = []
for keep, g in d.groupby("kept_features"):
    lo, hi = ci(g.auroc_penalty)
    agg.append(dict(kept_features=int(keep), k_aggr=KFIX, auroc_full=round(g.auroc_full.mean(), 4),
                    auroc_red=round(g.auroc_red.mean(), 4), auroc_penalty_mean=round(g.auroc_penalty.mean(), 4),
                    auroc_penalty_sd=round(g.auroc_penalty.std(), 4), ci_lo=lo, ci_hi=hi, n=len(g)))
pd.DataFrame(agg).to_csv(REPO / "results" / "p1_arcene_reverse_v3.csv", index=False)
print("WROTE p1_arcene_reverse_v3.csv (leakage-free, in-fold keep-selection)")
