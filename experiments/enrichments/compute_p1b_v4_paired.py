"""P1 Arm B v4 -- LEAKAGE-FREE, PAIRED across the ladder, and PARALLELISED.
(the pre-submission code review the final enrichment request item 2 + the second compute node: parallelise so it doesn't run on one core.)

v3 was leakage-free but derived the per-cell seed from {dataset,method,classifier,rep,KEEP}; because keep
was in the seed, every rung drew DIFFERENT folds, so the ladder was compared BETWEEN conditions -- the one
place in the study that departed from its own paired-by-construction design rule. v4 fix: DROP "keep" from
the seed dict, so within a (method,classifier,rep) every rung sees the IDENTICAL folds and the SAME base
ranking (nested pools), and the ladder becomes paired like every other comparison in the paper.

Parallelism note: the 900 cells (5 keeps x 3 rankers x 2 learners x 30 reps) are independent and each is
deterministic given its seed, so distributing them across worker processes changes ONLY the execution order,
never a value -- results are identical to the serial run. Each worker loads arcene once (cached per process),
and the RF ranker/classifier use n_jobs=1, so 16 cell-workers do not oversubscribe the 20 cores.
Same 30 reps x 3 rankers x {logistic,rf}, fixed k=25, per-unit rows + bootstrap CI. Frozen code untouched.
"""
import sys, os, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
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
NJOBS = int(os.environ.get("XNSVAD_NJOBS", "16"))


def clf(name, seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    return LogisticRegression(max_iter=2000, random_state=seed) if name == "logistic" \
        else RandomForestClassifier(n_estimators=150, random_state=seed, n_jobs=1)


def cell(X, y, keep, method, cname, rep):
    seed = derive_seed(MASTER, {"dataset": "arcene", "method": method, "classifier": cname, "rep": rep})
    # NOTE: "keep" deliberately EXCLUDED from the seed -> all rungs in a (method,cname,rep) share folds
    # + base ranking (nested pools) -> the ladder is PAIRED by construction (v4 fix).
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


_CACHE = {}
def _get_data():
    """Load arcene once per worker process; also drop this worker to BELOW_NORMAL priority.
    NOTE: re-register the high-dim loaders HERE (not only at module level): under loky the task is
    cloudpickled by value, so the worker does not execute the module's top-level LOADERS.update -- doing it
    inside the worker's first call guarantees data.load('arcene') resolves (fixes KeyError: 'arcene')."""
    if "X" not in _CACHE:
        try:
            import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
        except Exception:
            pass
        data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)   # ensure registered in this worker process
        X, y, _ = data.load("arcene"); X.attrs["name"] = "arcene"
        _CACHE["X"], _CACHE["y"] = X, np.asarray(y)
    return _CACHE["X"], _CACHE["y"]


def run_one(keep, method, cname, rep):
    X, y = _get_data()
    af, ar = cell(X, y, keep, method, cname, rep)
    return dict(kept_features=keep, method=method, classifier=cname, rep=rep,
                auroc_full=af, auroc_red=ar, auroc_penalty=af - ar)


def ci(v, seed=20260626, B=5000):  # 5000 to match stats.py BOOTSTRAP_DEFAULT (agent the Arm B v4 pre-specification)
    v = np.asarray(v, float); rng = np.random.RandomState(seed)
    bs = [v[rng.randint(0, len(v), len(v))].mean() for _ in range(B)]
    return round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)


if __name__ == "__main__":
    from joblib import Parallel, delayed
    tasks = [(keep, method, cname, rep)
             for keep in KEEPS for method in METHODS for cname in CLFS for rep in range(REPS)]
    print(f"Arm B v4 (paired) -- {len(tasks)} cells on {NJOBS} workers", flush=True)
    rows = Parallel(n_jobs=NJOBS, backend="loky", verbose=10)(delayed(run_one)(*t) for t in tasks)
    d = pd.DataFrame(rows).sort_values(["kept_features", "method", "classifier", "rep"]).reset_index(drop=True)
    d.to_csv(REPO / "results" / "p1_arcene_reverse_v4_rows.csv", index=False)
    for keep in KEEPS:
        g = d[d.kept_features == keep]
        print(f"  keep {keep:5d}: full={g.auroc_full.mean():.4f} red25={g.auroc_red.mean():.4f} "
              f"penalty={g.auroc_penalty.mean():+.4f} (sd {g.auroc_penalty.std():.4f})", flush=True)
    agg = []
    for keep, g in d.groupby("kept_features"):
        lo, hi = ci(g.auroc_penalty)
        agg.append(dict(kept_features=int(keep), k_aggr=KFIX, auroc_full=round(g.auroc_full.mean(), 4),
                        auroc_red=round(g.auroc_red.mean(), 4),
                        auroc_penalty_mean=round(g.auroc_penalty.mean(), 4),
                        auroc_penalty_sd=round(g.auroc_penalty.std(), 4), ci_lo=lo, ci_hi=hi, n=len(g)))
    pd.DataFrame(agg).to_csv(REPO / "results" / "p1_arcene_reverse_v4.csv", index=False)
    print("WROTE p1_arcene_reverse_v4.csv (leakage-free, in-fold keep-selection, PAIRED folds, parallel)", flush=True)
