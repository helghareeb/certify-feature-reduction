"""Tier 1 analysis from OOF probability caches (results/cache/poof/*.parquet).
T1.2  ECE reduction penalty (full frac:1 vs 25% frac:0.25) across bin counts {5,10,15,20,30,50},
      equal-width AND equal-frequency -> table bins x learner x calibrator; flag any direction/materiality flip.
T1.3  AURC reduction penalty under confidence = |p-0.5| (margin), predictive entropy, and margin |2p-1|
      -> show whether the penalty survives (expected: identical, since all are monotone in |p-0.5| for binary).
Matches src/nsclinfs/metrics.py exactly for equal-width ECE and trapezoid AURC.
Outputs: results/tier1/tier1_ece_binsweep.csv, tier1_aurc_confidence.csv, and prints a summary.
"""
import os as _os
# Repo root resolved from this file rather than hard-coded: the as-run copy carried an
# absolute path to the machine that produced it. Override with NSCLINFS_REPO if needed.
_REPO_ROOT = _os.environ.get('NSCLINFS_REPO') or _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glob, os, re, warnings
import numpy as np, pandas as pd
np.seterr(all="ignore"); warnings.filterwarnings("ignore")

POOF = glob.glob(_os.path.join(_REPO_ROOT, "results/cache/poof/*.parquet"))
FULL, RED = "frac:1", "frac:0.25"
BINS = [5, 10, 15, 20, 30, 50]
EPS = 1e-12

def ece_equal_width(y, p, bins):
    edges = np.linspace(0.0, 1.0, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    n = len(y); e = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            e += (m.sum()/n) * abs(y[m].mean() - p[m].mean())
    return e

def ece_equal_freq(y, p, bins):
    # quantile edges; each bin ~equal count (ties collapse bins, standard behavior)
    qs = np.quantile(p, np.linspace(0, 1, bins + 1))
    qs[0], qs[-1] = -np.inf, np.inf
    idx = np.clip(np.digitize(p, qs[1:-1]), 0, bins - 1)
    n = len(y); e = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            e += (m.sum()/n) * abs(y[m].mean() - p[m].mean())
    return e

def aurc(y, p, conf):
    yhat = (p >= 0.5).astype(int); err = (yhat != y).astype(float)
    order = np.argsort(-conf, kind="mergesort")
    risks = np.cumsum(err[order]) / np.arange(1, len(y)+1)
    cov = np.arange(1, len(y)+1) / len(y)
    return float(np.trapezoid(risks, cov))

def conf_margin(p):   return np.abs(p - 0.5)
def conf_entropy(p):
    pc = np.clip(p, EPS, 1-EPS)
    return -( -(pc*np.log(pc) + (1-pc)*np.log(1-pc)) )   # -H : higher = more confident
def conf_margin2(p):  return np.abs(2*p - 1)

rows_ece, rows_aurc = [], []
n_cells = 0
for f in POOF:
    name = os.path.basename(f)[:-8]
    ds, method, clf, cal, rep = name.split("__")
    df = pd.read_parquet(f, columns=["y", FULL, RED])
    y = df["y"].to_numpy().astype(int)
    pf, pr = df[FULL].to_numpy(), df[RED].to_numpy()
    n_cells += 1
    # T1.2 ECE penalties
    for bins in BINS:
        rows_ece.append(dict(dataset=ds, method=method, classifier=clf, calibrate=cal, rep=int(rep[3:]),
            bins=bins, bin_type="equal_width",
            ece_full=ece_equal_width(y,pf,bins), ece_red=ece_equal_width(y,pr,bins)))
        rows_ece.append(dict(dataset=ds, method=method, classifier=clf, calibrate=cal, rep=int(rep[3:]),
            bins=bins, bin_type="equal_freq",
            ece_full=ece_equal_freq(y,pf,bins), ece_red=ece_equal_freq(y,pr,bins)))
    # T1.3 AURC penalties under 3 confidence measures
    for cname, cfn in (("margin_abs_p_0.5",conf_margin),("pred_entropy",conf_entropy),("margin_2p_1",conf_margin2)):
        rows_aurc.append(dict(dataset=ds, method=method, classifier=clf, calibrate=cal, rep=int(rep[3:]),
            confidence=cname, aurc_full=aurc(y,pf,cfn(pf)), aurc_red=aurc(y,pr,cfn(pr))))

ece = pd.DataFrame(rows_ece); ece["penalty"] = ece["ece_red"] - ece["ece_full"]
aur = pd.DataFrame(rows_aurc); aur["penalty"] = aur["aurc_red"] - aur["aurc_full"]
print(f"cells loaded: {n_cells}  ece rows: {len(ece)}  aurc rows: {len(aur)}")

# ---- T1.2 table: mean penalty by classifier x calibrate x bins x bin_type (aggregated over datasets/methods/reps) ----
g = (ece.groupby(["classifier","calibrate","bin_type","bins"])
        .agg(mean_penalty=("penalty","mean"), std=("penalty","std"),
             frac_positive=("penalty", lambda s:(s>0).mean()), n=("penalty","size"),
             n_datasets=("dataset","nunique"))
        .reset_index())
g.to_csv(_os.path.join(_REPO_ROOT, "results/tier1/tier1_ece_binsweep.csv"), index=False)

# direction/materiality stability vs the bins=15 equal_width baseline (manuscript setting)
print("\n=== T1.2 ECE reduction penalty (mean over 12ds x 3methods x 30reps) — direction check ===")
flips = []
for (clf,cal),sub in g[g.bin_type=="equal_width"].groupby(["classifier","calibrate"]):
    signs = {int(r.bins): (1 if r.mean_penalty>0 else (-1 if r.mean_penalty<0 else 0)) for r in sub.itertuples()}
    base = signs.get(15)
    stable = all(v==base for v in signs.values())
    vals = " ".join(f"b{b}:{signs[b]:+d}({g[(g.classifier==clf)&(g.calibrate==cal)&(g.bin_type=='equal_width')&(g.bins==b)].mean_penalty.iloc[0]:+.4f})" for b in BINS)
    print(f"  {clf:8s} {cal:9s} base(b15)={base:+d} stable={stable}  {vals}")
    if not stable: flips.append((clf,cal,"equal_width"))
# equal_freq direction summary
for (clf,cal),sub in g[g.bin_type=="equal_freq"].groupby(["classifier","calibrate"]):
    signs = {int(r.bins): (1 if r.mean_penalty>0 else -1) for r in sub.itertuples()}
    base = signs.get(15); stable = all(v==base for v in signs.values())
    if not stable: flips.append((clf,cal,"equal_freq"))
print(f"\nDIRECTION FLIPS across bin counts: {flips if flips else 'NONE — every ECE penalty keeps its sign across {5..50} and both binnings'}")

# ---- T1.3 table: mean AURC penalty by classifier x calibrate x confidence ----
ga = (aur.groupby(["classifier","calibrate","confidence"])
         .agg(mean_penalty=("penalty","mean"), std=("penalty","std"),
              mean_aurc_full=("aurc_full","mean"), mean_aurc_red=("aurc_red","mean"), n=("penalty","size"))
         .reset_index())
ga.to_csv(_os.path.join(_REPO_ROOT, "results/tier1/tier1_aurc_confidence.csv"), index=False)
print("\n=== T1.3 AURC reduction penalty by confidence measure (mean over all cells) ===")
piv = ga.pivot_table(index=["classifier","calibrate"], columns="confidence", values="mean_penalty")
print(piv.round(6).to_string())
# invariance check: are the three confidence measures identical (monotone => same AURC)?
maxspread = (piv.max(axis=1) - piv.min(axis=1)).abs().max()
print(f"\nmax spread of AURC penalty across the 3 confidence measures = {maxspread:.3e}")
print("=> " + ("IDENTICAL (monotone-invariant): the AURC penalty survives unchanged; confirms the manuscript's 'move in tandem' concession."
              if maxspread < 1e-9 else f"NOT identical (spread {maxspread:.3e}) — that is the finding, report it."))
