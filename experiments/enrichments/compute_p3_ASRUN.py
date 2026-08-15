# P3 (safe-budget diagnostic) -- AS-RUN inline snippet. Thresholds pre-registered in PRESPEC_p3.md
# BEFORE this ran (saturation 0.90 rf-importance top-k share; spike = AURC penalty>=+0.02; unsafe iff b<k*).
import pandas as pd, numpy as np, json
R="results"; KS=[1,2,4,8,16,32,64,128,256]
conc=pd.read_csv(f"{R}/tier9_concentration.csv"); rf=conc[conc.ranker=="rf_importance"]
kstar={}
for _,row in rf.iterrows():
    ks=next((k for k in KS if row.get(f"top{k}_share",0)>=0.90), None); kstar[row.dataset]=ks if ks else int(row.p)
cl=pd.read_csv(f"{R}/summary.csv",comment="#")
hd={k:pd.read_csv(f"{R}/highdim/summary_{k}.csv",comment="#") for k in ["arrhythmia","prostate_ge","arcene","gli85"]}
def pen(ds,b):
    src=hd[ds] if ds in hd else cl; a=src[(src.outcome=="aurc")&(src.budget_type=="k")&(src.k_features==b)]
    return a.delta.mean() if len(a) else np.nan
rows=[]
for ds in kstar:
    for b in (KS if ds in hd else [1,2,4,8]):
        p=pen(ds,b)
        if not pd.isna(p): rows.append({"dataset":ds,"budget":b,"kstar":kstar[ds],"pred_unsafe":b<kstar[ds],"obs_spike":float(p)>=0.02})
d=pd.DataFrame(rows); print("agreement",(d.pred_unsafe==d.obs_spike).mean())
# NOTE: reads delivered summaries + tier9 concentration (rankings are TRAIN-fold in the runner); cache-only here.
