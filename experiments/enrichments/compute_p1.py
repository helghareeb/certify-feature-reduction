"""P1 -- probe-injection dose-response (approved enrichment; the one new-compute one).
Arm A: inject Gaussian noise features to DILUTE concentration at fixed n and true signal, measure the
reduction penalty vs dose. Arm B: keep the top-k rf features on arcene to RAISE concentration, measure
harm falling. Design locked in PRESPEC_p1.md. Reuses nsclinfs primitives; frozen code untouched.
"""
import sys, os, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
if os.environ.get("XNSVAD_LOW_PRIORITY") == "1":
    try:
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception: pass
warnings.filterwarnings("ignore"); np.seterr(all="ignore")
REPO = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(REPO / "src"))
from nsclinfs import data, reduction, highdim_data
from nsclinfs.seeds import derive_seed
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)

MASTER, NFOLDS, REPS = 20260626, 5, 30
METHODS = ["mutual_info", "rf_importance", "l1_logistic"]
CLFS = ["logistic", "rf"]


def aurc(y, p, conf):
    yhat = (p >= 0.5).astype(int); err = (yhat != y).astype(float)
    order = np.argsort(-conf, kind="mergesort")
    return float(np.trapezoid(np.cumsum(err[order]) / np.arange(1, len(y) + 1), np.arange(1, len(y) + 1) / len(y)))


def clf(name, seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    return LogisticRegression(max_iter=2000, random_state=seed) if name == "logistic" \
        else RandomForestClassifier(n_estimators=150, random_state=seed, n_jobs=1)


def oof_full_and_reduced(X, y, method, cname, rep, k_aggr):
    """OOF probs for full (all cols) and reduced (top-k_aggr), plus top-k concentration share."""
    seed = derive_seed(MASTER, {"dataset": X.attrs.get("name"), "method": method, "classifier": cname, "rep": rep})
    skf = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=seed)
    n = len(y); p_full = X.shape[1]
    p_oof_full, p_oof_red = np.full(n, np.nan), np.full(n, np.nan); shares = []
    for tr, te in skf.split(X, y):
        med = X.iloc[tr].median(numeric_only=True)
        Xtr, Xte = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
        ranking = reduction.rank(method, Xtr, y[tr], seed)
        for feats, dst in ((ranking, p_oof_full), (ranking[:k_aggr], p_oof_red)):
            mu, sd = Xtr[feats].mean(), Xtr[feats].std(ddof=0).replace(0.0, 1.0)
            Xtr_z, Xte_z = (Xtr[feats] - mu) / sd, (Xte[feats] - mu) / sd
            m = clf(cname, seed).fit(Xtr_z, y[tr])
            dst[te] = m.predict_proba(Xte_z)[:, 1]
    return p_oof_full, p_oof_red


def evaluate(X, y, k_aggr, tag):
    """Mean over methods x classifiers x reps of AUROC(full/reduced) + penalties."""
    rows = []
    for method in METHODS:
        for cname in CLFS:
            for rep in range(REPS):
                pf, pr = oof_full_and_reduced(X, y, method, cname, rep, k_aggr)
                ok = ~np.isnan(pf) & ~np.isnan(pr)
                af, ar = roc_auc_score(y[ok], pf[ok]), roc_auc_score(y[ok], pr[ok])
                uf = aurc(y[ok], pf[ok], np.abs(pf[ok] - 0.5)); ur = aurc(y[ok], pr[ok], np.abs(pr[ok] - 0.5))
                rows.append(dict(auroc_full=af, auroc_red=ar, aurc_full=uf, aurc_red=ur))
    d = pd.DataFrame(rows)
    return dict(tag=tag, auroc_full=d.auroc_full.mean(), auroc_red=d.auroc_red.mean(),
                auroc_penalty=d.auroc_full.mean() - d.auroc_red.mean(),
                aurc_penalty=d.aurc_red.mean() - d.aurc_full.mean())


# ---- Arm A: probe injection ----
resA = []
for ds in ["cleveland", "mammographic", "spectf"]:
    X0, y, _ = data.load(ds); p0 = X0.shape[1]; k_aggr = max(1, round(0.25 * p0))
    for dose in [0, 1, 2, 5, 10]:
        if dose == 0:
            X = X0.copy()
        else:
            rng = np.random.RandomState(derive_seed(MASTER, {"probe": 1, "dataset": ds, "dose": dose}))
            G = pd.DataFrame(rng.standard_normal((len(y), dose * p0)),
                             columns=[f"probe{i}" for i in range(dose * p0)])
            X = pd.concat([X0.reset_index(drop=True), G], axis=1)
        X.attrs["name"] = f"{ds}_dose{dose}"
        r = evaluate(X, np.asarray(y), k_aggr, f"{ds}_dose{dose}")
        r.update(dataset=ds, dose=dose, p_full=X.shape[1], k_aggr=k_aggr)
        resA.append(r)
        print(f"  A {ds:12s} dose{dose:2d}x p={X.shape[1]:4d} k={k_aggr:3d}  "
              f"auroc_red={r['auroc_red']:.3f} auroc_pen={r['auroc_penalty']:+.3f} aurc_pen={r['aurc_penalty']:+.3f}")
dfA = pd.DataFrame(resA); dfA.to_csv(REPO / "results" / "p1_probe_injection.csv", index=False)

# ---- Arm B: reverse concentration on arcene (keep top-k rf features) ----
resB = []
Xa, ya, _ = data.load("arcene"); Xa.attrs["name"] = "arcene"; ya = np.asarray(ya)
# rank once (rf_importance, full data, seed) to define the top-k feature sets
rk = reduction.rank("rf_importance", Xa.fillna(Xa.median(numeric_only=True)), ya, MASTER)
for keep in [100, 256, 1000, 5000, Xa.shape[1]]:
    feats = rk[:keep]
    Xk = Xa[feats].copy(); Xk.attrs["name"] = f"arcene_keep{keep}"
    k_aggr = max(1, round(0.25 * keep))
    r = evaluate(Xk, ya, k_aggr, f"arcene_keep{keep}")
    r.update(kept_features=keep, k_aggr=k_aggr)
    resB.append(r)
    print(f"  B arcene keep{keep:5d}  k={k_aggr:4d}  auroc_red={r['auroc_red']:.3f} "
          f"auroc_pen={r['auroc_penalty']:+.3f} aurc_pen={r['aurc_penalty']:+.3f}")
dfB = pd.DataFrame(resB); dfB.to_csv(REPO / "results" / "p1_arcene_reverse.csv", index=False)

json.dump({"armA_note": "probe injection; harm vs dose", "armB_note": "arcene keep-top-k; harm vs concentration"},
          open(REPO / "results" / "p1_summary.json", "w"), indent=2)
print("\nWROTE p1_probe_injection.csv + p1_arcene_reverse.csv")
