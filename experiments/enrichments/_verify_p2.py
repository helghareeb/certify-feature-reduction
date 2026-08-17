import glob, os, numpy as np, pandas as pd, sys, json
sys.path.insert(0,"src")
from nsclinfs.metrics import expected_calibration_error as ece_fn
rows=[]
for f in glob.glob("results/cache/poof/*.parquet"):
    ds,method,clf,cal,rep=os.path.basename(f)[:-8].split("__")
    if cal not in ("none","sigmoid","isotonic"): continue
    d=pd.read_parquet(f,columns=["y","frac:1"]); y=d["y"].to_numpy().astype(int); p=d["frac:1"].to_numpy()
    rows.append((cal,ece_fn(y,p)))
df=pd.DataFrame(rows,columns=["calibrate","ece"])
m=df.groupby("calibrate").ece.mean()
out={"n_cells_total":len(df),"mean_ece":{k:round(float(v),4) for k,v in m.items()},
     "ece_recovery_sigmoid":round(float(m['none']-m['sigmoid']),4),
     "ece_recovery_isotonic":round(float(m['none']-m['isotonic']),4)}
json.dump(out,open("results/p2_verify_allranker_ece.json","w"),indent=2)
print(json.dumps(out,indent=2))
