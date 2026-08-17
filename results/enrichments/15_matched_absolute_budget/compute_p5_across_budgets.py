"""P5 across matched budgets (the pre-submission code review enrichment item 1) -- cache-only re-analysis, no fitting.
Replicates the matched-absolute-budget width test at k in {1,2,4,8} instead of k=8 only, so the
nine-of-twelve restriction (k=8 forces out haberman/mammographic/pima) is lifted where the budget admits
all twelve. harm_auroc = AUROC(full) - AUROC(reduced-to-k) = -delta(auroc) at exact-k budget, per dataset,
CLINICAL PANEL ONLY (never pooled with the high-dimensional arm). Reports Spearman rho(p, harm) with p-value
AND a 5000-resample bootstrap CI (resampling datasets) at each budget. A dataset qualifies at budget k only
if p>k (genuine reduction). Reads results/summary.csv (the released per-configuration summary). Frozen code
untouched.
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
REPO = Path(__file__).resolve().parents[0]
S = pd.read_csv(REPO / "results" / "summary.csv", comment="#")
PMAP = pd.read_csv(REPO / "results" / "tier8_correlates_clinical.csv").set_index("dataset")["p"].to_dict()
BUDGETS = [1, 2, 4, 8]


def boot_ci(x, y, B=5000, seed=20260626):
    rng = np.random.RandomState(seed); n = len(x); vals = []
    for _ in range(B):
        idx = rng.randint(0, n, n)
        if len(np.unique(x[idx])) < 3:  # need spread to define a rank correlation
            continue
        vals.append(spearmanr(x[idx], y[idx])[0])
    return round(float(np.nanpercentile(vals, 2.5)), 3), round(float(np.nanpercentile(vals, 97.5)), 3)


rows, summary = [], []
for k in BUDGETS:
    d = S[(S.budget == f"k:{k}") & (S.outcome == "auroc") & (S.calibrate == "none")]
    g = d.groupby("dataset").delta.mean()
    panel = [(ds, -float(g[ds]), int(PMAP[ds])) for ds in g.index if PMAP.get(ds, 0) > k]
    df = pd.DataFrame(panel, columns=["dataset", "harm_auroc", "p"])
    for _, r in df.iterrows():
        rows.append(dict(budget_k=k, dataset=r.dataset, p=int(r.p), harm_auroc=round(r.harm_auroc, 4)))
    rho, pv = spearmanr(df.harm_auroc, df.p)
    lo, hi = boot_ci(df.harm_auroc.to_numpy(), df.p.to_numpy())
    summary.append(dict(budget_k=k, n_datasets=len(df), spearman_rho=round(float(rho), 3),
                        p_value=round(float(pv), 4), boot_ci_lo=lo, boot_ci_hi=hi))

pd.DataFrame(rows).to_csv(REPO / "results" / "p5_width_rows.csv", index=False)
sdf = pd.DataFrame(summary); sdf.to_csv(REPO / "results" / "p5_width_across_budgets.csv", index=False)
json.dump({"panel": "clinical only (never pooled with high-dim)",
           "harm": "AUROC(full) - AUROC(reduced-to-k)",
           "results": summary}, open(REPO / "results" / "p5_width_across_budgets.json", "w"), indent=2)
print(sdf.to_string(index=False))
print("WROTE p5_width_across_budgets.csv/.json + p5_width_rows.csv")
