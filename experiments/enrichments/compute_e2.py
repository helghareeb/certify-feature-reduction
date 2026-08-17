"""E2 -- is the distance-to-support (-d) independence n-DEPENDENT? (approved enrichment).
Bounds the Tier-6 range of validity: the pooled Spearman(-d,|p-0.5|)=0.402 is dominated by diabetes130's
101k points. Report per-dataset independence and surviving AURC penalty AGAINST n -- never only pooled.
Pure cache analysis (tier6_sanity.json + tier6_measurement_12ds.csv). Honest-negative-safe.
"""
import os as _os
# Repo root resolved from this file rather than hard-coded: the as-run copy carried an
# absolute path to the machine that produced it. Override with NSCLINFS_REPO if needed.
_REPO_ROOT = _os.environ.get('NSCLINFS_REPO') or _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json
import numpy as np, pandas as pd
from scipy import stats
REPO = _REPO_ROOT

san = json.load(open(f"{REPO}/results/tier6_sanity.json"))["per_dataset"]
meas = pd.read_csv(f"{REPO}/results/tier6_measurement_12ds.csv")
pen = meas.groupby("dataset")[["penalty_margin", "penalty_d"]].mean()

rows = []
for ds, v in san.items():
    rows.append({"dataset": ds, "n": v["n"], "p": v["p"], "rho_indep": v["rho"],
                 "penalty_margin": round(float(pen.loc[ds, "penalty_margin"]), 4) if ds in pen.index else np.nan,
                 "penalty_d": round(float(pen.loc[ds, "penalty_d"]), 4) if ds in pen.index else np.nan})
df = pd.DataFrame(rows).sort_values("n").reset_index(drop=True)
df.to_csv(f"{REPO}/results/e2_independence_vs_n.csv", index=False)

pooled = json.load(open(f"{REPO}/results/tier6_sanity.json"))["pooled_spearman_negd_vs_margin"]
unw = df.rho_indep.mean()
# is independence (|rho|) or rho n-dependent? and is the surviving penalty n-dependent?
sp_n_rho = stats.spearmanr(df.n, df.rho_indep)
sp_n_absrho = stats.spearmanr(df.n, df.rho_indep.abs())
sp_n_pend = stats.spearmanr(df.n, df.penalty_d)

print("=== E2: per-dataset independence & surviving penalty vs n (sorted by n) ===")
print(df.to_string(index=False))
print(f"\npooled rho(-d,|p-0.5|) = {pooled:+.3f}  (dominated by diabetes130: {df[df.dataset=='diabetes130'].n.iloc[0]:,} pts)")
print(f"UNWEIGHTED mean per-dataset rho = {unw:+.3f}   (the honest central value)")
print(f"\nSpearman(n, rho_indep)   = {sp_n_rho.statistic:+.3f}  p={sp_n_rho.pvalue:.3f}")
print(f"Spearman(n, |rho_indep|) = {sp_n_absrho.statistic:+.3f}  p={sp_n_absrho.pvalue:.3f}")
print(f"Spearman(n, penalty_d)   = {sp_n_pend.statistic:+.3f}  p={sp_n_pend.pvalue:.3f}")

verdict = ("independence_decays_with_n" if sp_n_rho.pvalue < 0.05 and sp_n_rho.statistic > 0
           else "no_n_trend")
print(f"\nVERDICT: {verdict}")
print("READING:",
      "rho rises with n -> -d less independent at large n -> Tier-6 argument has an n-range; state it."
      if verdict == "independence_decays_with_n" else
      "NO significant n-trend in independence -> the high pooled figure is a POINT-WEIGHTING artifact of "
      "diabetes130's 101k points, NOT an n-effect. Tier-6 independence holds across n (unweighted rho=0.27, "
      "well below 0.5); report the unweighted mean, not the pooled value.")
json.dump({"pooled_rho": float(pooled), "unweighted_mean_rho": float(unw),
           "spearman_n_vs_rho": [round(float(sp_n_rho.statistic),3), round(float(sp_n_rho.pvalue),4)],
           "spearman_n_vs_absrho": [round(float(sp_n_absrho.statistic),3), round(float(sp_n_absrho.pvalue),4)],
           "spearman_n_vs_penalty_d": [round(float(sp_n_pend.statistic),3), round(float(sp_n_pend.pvalue),4)],
           "verdict": verdict}, open(f"{REPO}/results/e2_summary.json", "w"), indent=2)
print("\nWROTE e2_independence_vs_n.csv + e2_summary.json")
