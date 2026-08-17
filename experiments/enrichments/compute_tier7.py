"""Tier 7 aggregation — reduction penalty vs n at FIXED p=279 (arrhythmia).
Reads the four validated summaries (n=100,150,250 from results/tier7/, n=452 from the existing
results/highdim/summary_arrhythmia.csv) and builds the penalty-vs-n table in the same shape as the
Tier-2 partial: AUROC delta at aggressive budgets + mean over k-arm, and AURC mean-delta (k-arm),
per classifier. If harm shrinks/flips as n falls at fixed p, the boundary is in n/p, not p.
"""
import sys, pandas as pd, numpy as np
from pathlib import Path
REPO = Path(__file__).resolve().parents[0]
P = 279
SRC = {100: REPO/"results/tier7/summary_arrhythmia_n100.csv",
       150: REPO/"results/tier7/summary_arrhythmia_n150.csv",
       250: REPO/"results/tier7/summary_arrhythmia_n250.csv",
       452: REPO/"results/highdim/summary_arrhythmia.csv"}

def load(fn):
    return pd.read_csv(fn, comment="#")

rows = []
for n, fn in SRC.items():
    if not Path(fn).exists():
        print(f"  MISSING n={n}: {fn} (run run_tier7.sh first)"); continue
    df = load(fn)
    for clf in sorted(df.classifier.unique()):
        a = df[(df.outcome == "auroc") & (df.budget_type == "k") & (df.classifier == clf)]
        u = df[(df.outcome == "aurc") & (df.budget_type == "k") & (df.classifier == clf)]
        d_k1 = a[a.k_features == 1].delta.mean()
        d_k8 = a[a.k_features == 8].delta.mean()
        rows.append({"n": n, "n_over_p": round(n/P, 3), "classifier": clf,
                     "auroc_delta_k1": round(d_k1, 4), "auroc_delta_k8": round(d_k8, 4),
                     "auroc_delta_karm_mean": round(a.delta.mean(), 4),
                     "aurc_delta_karm_mean": round(u.delta.mean(), 4)})
out = pd.DataFrame(rows)
if len(out):
    out.to_csv(REPO/"results/tier7/tier7_penalty_vs_n.csv", index=False)
    print(out.to_string(index=False))
    print("\nWROTE results/tier7/tier7_penalty_vs_n.csv")
    # verdict helper: does harm at k=8 shrink toward 0 (or flip +) as n falls?
    for clf in sorted(out.classifier.unique()):
        s = out[out.classifier == clf].sort_values("n")
        print(f"  {clf}: auroc_delta_k8 by n {list(zip(s.n, s.auroc_delta_k8))}")
else:
    print("No summaries yet.")
