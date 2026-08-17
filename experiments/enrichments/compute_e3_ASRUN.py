# E3 (cross-axis coherence) -- AS-RUN inline snippet (CORRECTED orientation: conformal_efficiency=set size,
# lower better -> +delta worse; all off-diagonals asserted positive).
import pandas as pd, numpy as np, json
R="results"; cl=pd.read_csv(f"{R}/summary.csv",comment="#")
agg=cl[(cl.budget_type=="frac")&(cl.frac==0.25)]
axes={"ECE":("ece",+1),"AURC":("aurc",+1),"net_benefit":("net_benefit",-1),
      "conformal_setsize":("conformal_efficiency",+1),"selective_ECE":("selective_ece",+1)}
key=["dataset","method","classifier"]; mats={}
for name,(oc,sign) in axes.items():
    s=agg[agg.outcome==oc][key+["delta"]].copy(); s["harm"]=sign*s["delta"]; mats[name]=s.set_index(key)["harm"]
M=pd.DataFrame(mats).dropna(); corr=M.corr(method="spearman").round(3)
off=corr.where(~np.eye(len(corr),dtype=bool)).stack().dropna()
assert bool((off>0).all()), "orientation error: off-diagonal negative under harm-orientation"
corr.to_csv(f"{R}/e3_cross_axis_corr.csv"); print(corr.to_string())
# NOTE: cache-only over delivered summaries; no CV/fit/selection -> no leakage surface.
