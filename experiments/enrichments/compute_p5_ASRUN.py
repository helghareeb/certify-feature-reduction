# P5 (absolute vs fractional k) -- AS-RUN inline snippet.
import pandas as pd, numpy as np, json
from scipy import stats
R="results"
cl=pd.read_csv(f"{R}/summary.csv",comment="#")
hd_sets=[("arrhythmia",279,452),("prostate_ge",5966,102),("arcene",10000,200),("gli85",22283,85)]
rows=[]
for ds in cl.dataset.unique():
    a=cl[(cl.dataset==ds)&(cl.outcome=="auroc")&(cl.budget_type=="k")&(cl.k_features==8)]
    if len(a): rows.append({"dataset":ds,"block":"clinical","p":int(a.n_features.iloc[0]),"harm_auroc_k8":round(-a.delta.mean(),4)})
for ds,p,n in hd_sets:
    h=pd.read_csv(f"{R}/highdim/summary_{ds}.csv",comment="#")
    a=h[(h.outcome=="auroc")&(h.budget_type=="k")&(h.k_features==8)]
    if len(a): rows.append({"dataset":ds,"block":"highdim","p":p,"harm_auroc_k8":round(-a.delta.mean(),4)})
d=pd.DataFrame(rows).sort_values("p"); d.to_csv(f"{R}/p5_harm_at_absolute_k8.csv",index=False)
print("Spearman(p,harm@k8) all:",stats.spearmanr(d.p,d.harm_auroc_k8))
# NOTE: reads DELIVERED summaries (frozen-runner outputs, in-fold safe); pure arithmetic -> no new leakage surface.
