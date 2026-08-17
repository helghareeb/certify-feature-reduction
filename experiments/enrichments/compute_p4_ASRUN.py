# P4 (localize surviving 35%) -- AS-RUN inline snippet (was executed via heredoc, not a saved file).
import pandas as pd, numpy as np, json
from scipy import stats
meas=pd.read_csv("results/tier6_measurement_12ds.csv")
pend=meas.groupby("dataset")[["penalty_margin","penalty_d"]].mean()
conc=pd.read_csv("results/tier9_concentration.csv")
gini_rf=conc[conc.ranker=="rf_importance"].set_index("dataset")["gini"]
t8=pd.read_csv("results/tier8_correlates_clinical.csv").set_index("dataset")[["retained_k_aggr","p"]]
rows=[]
for ds in pend.index:
    if ds in gini_rf.index and ds in t8.index:
        rows.append({"dataset":ds,"penalty_d":round(pend.loc[ds,"penalty_d"],4),
                     "gini_rf":round(float(gini_rf[ds]),3),"retained_k":float(t8.loc[ds,"retained_k_aggr"]),"p":int(t8.loc[ds,"p"])})
d=pd.DataFrame(rows); d.to_csv("results/p4_surviving_vs_concentration.csv",index=False)
for x in ["gini_rf","retained_k","p"]:
    rho,pv=stats.spearmanr(d.penalty_d,d[x]); print(f"Spearman(penalty_d, {x}) = {rho:+.3f} p={pv:.3f}")
# NOTE: cache-only; no CV, no model fit, no label-informed selection -> no leakage surface.
