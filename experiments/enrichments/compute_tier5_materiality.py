"""Tier 1 — materiality of the ECE bin-sweep (review's follow-up).
Q: is the logistic ECE-penalty sign flip MATERIAL (Holm-corrected) at any bin count, or noise?
   where is the crossover, and does equal-frequency binning move it?
Test: unit = (dataset, method); unit penalty = mean over 30 reps of [ECE_bin(frac:0.25) - ECE_bin(frac:1)].
      one-sample t-test (and Wilcoxon) of unit penalties vs 0, per (classifier,calibrate,bin_type,bins);
      Holm correction across the 6 bin counts (the sweep family). Material if p_holm < stat_alpha.
"""
import os as _os
# Repo root resolved from this file rather than hard-coded: the as-run copy carried an
# absolute path to the machine that produced it. Override with NSCLINFS_REPO if needed.
_REPO_ROOT = _os.environ.get('NSCLINFS_REPO') or _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glob, os, json, warnings
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
np.seterr(all="ignore"); warnings.filterwarnings("ignore")

REPO = _REPO_ROOT
POOF = glob.glob(os.path.join(REPO, r"results\cache\poof\*.parquet"))
FULL, RED = "frac:1", "frac:0.25"
BINS = [5,10,15,20,30,50]
ALPHA = json.load(open(os.path.join(REPO,"config","calibration.json"))).get("stat_alpha",0.05)

def ece_ew(y,p,b):
    e=np.linspace(0,1,b+1); idx=np.clip(np.digitize(p,e[1:-1]),0,b-1); n=len(y); s=0.0
    for k in range(b):
        m=idx==k
        if m.any(): s+=(m.sum()/n)*abs(y[m].mean()-p[m].mean())
    return s
def ece_ef(y,p,b):
    q=np.quantile(p,np.linspace(0,1,b+1)); q[0],q[-1]=-np.inf,np.inf
    idx=np.clip(np.digitize(p,q[1:-1]),0,b-1); n=len(y); s=0.0
    for k in range(b):
        m=idx==k
        if m.any(): s+=(m.sum()/n)*abs(y[m].mean()-p[m].mean())
    return s

pen_path = os.path.join(REPO,"results","tier5","ece_penalties_gb.parquet")
if os.path.exists(pen_path):
    df = pd.read_parquet(pen_path)
else:
    rows=[]
    for f in POOF:
        ds,method,clf,cal,rep=os.path.basename(f)[:-8].split("__")
        if clf != "gb":  # TIER 5: gradient boosting only
            continue
        d=pd.read_parquet(f,columns=["y",FULL,RED]); y=d["y"].to_numpy().astype(int)
        pf,pr=d[FULL].to_numpy(),d[RED].to_numpy()
        for b in BINS:
            rows.append((ds,method,clf,cal,int(rep[3:]),b,"equal_width", ece_ew(y,pr,b)-ece_ew(y,pf,b)))
            rows.append((ds,method,clf,cal,int(rep[3:]),b,"equal_freq",  ece_ef(y,pr,b)-ece_ef(y,pf,b)))
    df=pd.DataFrame(rows,columns=["dataset","method","classifier","calibrate","rep","bins","bin_type","penalty"])
    df.to_parquet(pen_path)
print(f"penalty rows: {len(df)}  stat_alpha={ALPHA}")

# unit = (dataset,method) mean over reps
unit = df.groupby(["classifier","calibrate","bin_type","bins","dataset","method"])["penalty"].mean().reset_index()

out=[]
for (clf,cal,bt),sub in unit.groupby(["classifier","calibrate","bin_type"]):
    ps=[]; recs=[]
    for b in BINS:
        v=sub[sub.bins==b]["penalty"].to_numpy()
        mean=v.mean(); t_p=stats.ttest_1samp(v,0.0).pvalue
        try: w_p=stats.wilcoxon(v).pvalue
        except Exception: w_p=np.nan
        ps.append(t_p); recs.append((b,mean,len(v),t_p,w_p))
    holm=multipletests(ps,method="holm")[1]
    for (b,mean,n,t_p,w_p),hp in zip(recs,holm):
        out.append(dict(classifier=clf,calibrate=cal,bin_type=bt,bins=b,mean_penalty=round(mean,5),
                        n_units=n,sign=("+" if mean>0 else "-"),p_ttest=round(t_p,4),p_wilcoxon=round(w_p,4),
                        p_holm=round(hp,4),material=bool(hp<ALPHA)))
res=pd.DataFrame(out)
res.to_csv(os.path.join(REPO,"results","tier5","tier5_ece_materiality.csv"),index=False)

print("\n=== ECE penalty materiality (Holm across the 6 bin counts) ===")
for (clf,cal,bt),s in res.groupby(["classifier","calibrate","bin_type"]):
    line=" ".join(f"b{r.bins}:{r.sign}{'*' if r.material else ' '}" for r in s.itertuples())
    print(f"  {clf:8s} {cal:9s} {bt:11s}  {line}   (* = material p_holm<{ALPHA})")

print("\n=== the gb/isotonic sign flip — detail ===")
for bt in ("equal_width","equal_freq"):
    s=res[(res.classifier=='gb')&(res.calibrate=='isotonic')&(res.bin_type==bt)].sort_values("bins")
    signs=list(s.sign); bins=list(s.bins)
    cross=[f"{bins[i]}->{bins[i+1]}" for i in range(len(bins)-1) if signs[i]!=signs[i+1]]
    print(f"  gb/isotonic {bt}: signs={dict(zip(bins,signs))}")
    print(f"     crossover(s): {cross if cross else 'none (no sign change)'}")
    for r in s.itertuples():
        print(f"     b{r.bins}: mean={r.mean_penalty:+.5f} p_holm={r.p_holm} material={r.material}")
