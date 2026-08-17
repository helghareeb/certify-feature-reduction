"""P6 -- combined-confidence audit (approved, reframed as audit; design locked in PRESPEC_p6.md).
Question: does a probability-INDEPENDENT confidence (-d) MITIGATE the measured AURC reduction penalty?
Three arms on the SAME cached OOF predictions: A=|p-0.5|, B=-d, C=combined (0.5*(rank01(|p-0.5|)+rank01(-d))
within each held-out fold). Report AURC penalty (aggressive frac:0.25 vs full frac:1) under A,B,C, all side
by side, over the 12 clinical datasets (T6.3 grid: 3 rankers x {logistic,rf} x 30 reps). Also selective net
benefit at coverage 0.8 over the committed NB threshold range. Reuses cached OOF + recomputes -d (no refit).
NOT tuned. Frozen code untouched.
"""
import sys, os, json, argparse, warnings
from pathlib import Path
import numpy as np, pandas as pd
if os.environ.get("XNSVAD_LOW_PRIORITY") == "1":
    try:
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception: pass
warnings.filterwarnings("ignore"); np.seterr(all="ignore")
REPO = Path(__file__).resolve().parents[0]; sys.path.insert(0, str(REPO / "src"))
from nsclinfs import data, highdim_data
from nsclinfs.seeds import derive_seed
from nsclinfs.metrics import mean_net_benefit
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import BallTree
data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)
CFG = json.load(open(REPO / "config" / "calibration.json"))
MASTER, NFOLDS, REPS, MNN = CFG["RANDOM_SEED"], CFG["n_folds"], CFG["REPS"], 10
METHODS = CFG["reduction_methods"]; DS_PARAMS = CFG.get("dataset_params", {})
NB = CFG["metric_params"]["net_benefit"]; NB_ARGS = (float(NB["t_lo"]), float(NB["t_hi"]), int(NB["n_thresholds"]))
POOF = REPO / "results" / "cache" / "poof"; FULL, AGGR = "frac:1", "frac:0.25"


def aurc(y, p, conf):
    yhat = (p >= 0.5).astype(int); err = (yhat != y).astype(float)
    order = np.argsort(-conf, kind="mergesort")
    return float(np.trapezoid(np.cumsum(err[order]) / np.arange(1, len(y) + 1), np.arange(1, len(y) + 1) / len(y)))


def rank01(x):
    r = pd.Series(x).rank(method="average").to_numpy() - 1.0
    return r / r.max() if r.max() > 0 else np.zeros_like(r)


def negd_and_folds(ds, method, clf, rep, y):
    """-d (X-only) OOF on the cell's folds + the fold index per point (for within-fold rank-norm)."""
    X, _, _ = data.load(ds, params=DS_PARAMS.get(ds)); X.attrs["name"] = ds
    seed = derive_seed(MASTER, {"dataset": ds, "method": method, "classifier": clf, "rep": rep})
    skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
    conf = np.full(len(y), np.nan); fold = np.full(len(y), -1, int)
    for fi, (tr, te) in enumerate(skf.split(X, y)):
        med = X.iloc[tr].median(numeric_only=True)
        Xtr, Xte = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
        mu, sd = Xtr.mean(), Xtr.std(ddof=0).replace(0.0, 1.0)
        tree = BallTree(((Xtr - mu) / sd).to_numpy(), metric="euclidean")
        dist, _ = tree.query(((Xte - mu) / sd).to_numpy(), k=MNN)
        conf[te] = -dist.mean(axis=1); fold[te] = fi
    return conf, fold


def combined_conf(margin, negd, fold):
    c = np.full(len(margin), np.nan)
    for fi in np.unique(fold):
        m = fold == fi
        c[m] = 0.5 * (rank01(margin[m]) + rank01(negd[m]))
    return c


def sel_nb(y, p, conf, coverage=0.8):
    """Mean net benefit on the top-`coverage` most-confident points (abstain the rest)."""
    k = max(1, int(round(coverage * len(y)))); keep = np.argsort(-conf, kind="mergesort")[:k]
    return mean_net_benefit(y[keep], p[keep], *NB_ARGS)


ap = argparse.ArgumentParser(); ap.add_argument("--datasets", default=""); a = ap.parse_args()
CLIN = [d for d in CFG["datasets"]]
run_list = [d.strip() for d in a.datasets.split(",") if d.strip()] or CLIN
rows = []
for ds in run_list:
    for method in METHODS:
        for clf in ("logistic", "rf"):
            for rep in range(REPS):
                f = POOF / f"{ds}__{method}__{clf}__none__rep{rep}.parquet"
                if not f.exists(): continue
                pdf = pd.read_parquet(f)
                if FULL not in pdf.columns or AGGR not in pdf.columns: continue
                y = pdf["y"].to_numpy().astype(int)
                negd, fold = negd_and_folds(ds, method, clf, rep, y); ok = ~np.isnan(negd)
                rec = {"dataset": ds, "method": method, "classifier": clf, "rep": rep}
                for bud, lbl in ((FULL, "full"), (AGGR, "aggr")):
                    p = pdf[bud].to_numpy(); margin = np.abs(p - 0.5)
                    comb = combined_conf(margin, negd, fold)
                    rec[f"aurc_A_{lbl}"] = aurc(y[ok], p[ok], margin[ok])
                    rec[f"aurc_B_{lbl}"] = aurc(y[ok], p[ok], negd[ok])
                    rec[f"aurc_C_{lbl}"] = aurc(y[ok], p[ok], comb[ok])
                    rec[f"selnb_A_{lbl}"] = sel_nb(y[ok], p[ok], margin[ok])
                    rec[f"selnb_C_{lbl}"] = sel_nb(y[ok], p[ok], comb[ok])
                rows.append(rec)
    print(f"  {ds}: cells so far = {len(rows)}")
df = pd.DataFrame(rows)
suffix = f"_{run_list[0]}" if len(run_list) == 1 else ""
df.to_csv(REPO / "results" / f"p6_arms{suffix}.csv", index=False)
if len(run_list) > 1:
    for arm in ("A", "B", "C"):
        pen = df[f"aurc_{arm}_aggr"].mean() - df[f"aurc_{arm}_full"].mean()
        print(f"  arm {arm}: mean AURC penalty = {pen:+.5f}")
    print(f"  selNB penalty A = {df.selnb_A_aggr.mean()-df.selnb_A_full.mean():+.5f}  "
          f"C = {df.selnb_C_aggr.mean()-df.selnb_C_full.mean():+.5f}")
print(f"WROTE p6_arms{suffix}.csv ({len(df)} cells)")
