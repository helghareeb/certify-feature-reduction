"""P2 -- flexibility ladder (approved enrichment, cache-only).
Order the 5 recalibrators by flexibility -- none(0) < temperature(1) < sigmoid(2) < beta(3) <
isotonic(nonparametric) -- and report RECOVERY (vs none) on three axes at full budget:
  ECE recovery      = ECE(none) - ECE(cal)      (positive = calibration recovered calibration error)
  AURC recovery     = AURC(none) - AURC(cal)     (positive = selective reliability recovered)
  net-benefit rec.  = NB(cal) - NB(none)         (positive = clinical utility recovered)
Prediction (§4.8): ECE recovery RISES with flexibility while AURC/NB recovery stays ~0 across all rungs.
Sources: summary_recalibration.csv (none/sigmoid/isotonic) + summary_tier3_{11ds,d130}.csv (none/beta/temp).
"""
import os as _os
# Repo root resolved from this file rather than hard-coded: the as-run copy carried an
# absolute path to the machine that produced it. Override with NSCLINFS_REPO if needed.
_REPO_ROOT = _os.environ.get('NSCLINFS_REPO') or _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import pandas as pd, numpy as np, json
R = _os.path.join(_REPO_ROOT, "results")
recal = pd.read_csv(f"{R}/summary_recalibration.csv", comment="#")
t3 = pd.concat([pd.read_csv(f"{R}/summary_tier3_11ds.csv", comment="#"),
                pd.read_csv(f"{R}/summary_tier3_d130.csv", comment="#")], ignore_index=True)

def mean_metric(df, cal, outcome):
    s = df[(df.calibrate == cal) & (df.budget_type == "frac") & (df.frac == 1.0) & (df.outcome == outcome)]
    return float(s["mean"].mean())

# sanity: the two files' 'none' baselines must agree (same grid/seeds)
for oc in ["ece", "aurc", "net_benefit"]:
    a, b = mean_metric(recal, "none", oc), mean_metric(t3, "none", oc)
    print(f"none baseline {oc}: recal={a:.5f} tier3={b:.5f} diff={abs(a-b):.2e}")

base = {oc: mean_metric(recal, "none", oc) for oc in ["ece", "aurc", "net_benefit"]}
src = {"none": recal, "temperature": t3, "sigmoid": recal, "beta": t3, "isotonic": recal}
ladder = ["none", "temperature", "sigmoid", "beta", "isotonic"]
flex = {"none": 0, "temperature": 1, "sigmoid": 2, "beta": 3, "isotonic": 99}

rows = []
for cal in ladder:
    df = src[cal]
    ece, aurc, nb = mean_metric(df, cal, "ece"), mean_metric(df, cal, "aurc"), mean_metric(df, cal, "net_benefit")
    rows.append({"calibrate": cal, "flexibility": flex[cal],
                 "ece": round(ece, 4), "ece_recovery": round(base["ece"] - ece, 4),
                 "aurc": round(aurc, 4), "aurc_recovery": round(base["aurc"] - aurc, 4),
                 "net_benefit": round(nb, 4), "nb_recovery": round(nb - base["net_benefit"], 4)})
out = pd.DataFrame(rows)
out.to_csv(f"{R}/p2_flexibility_ladder.csv", index=False)
print("\n=== P2 flexibility ladder (recovery vs none, at full budget, 12ds x 3rankers x 3learners) ===")
print(out.to_string(index=False))

# does ECE recovery rise monotonically while AURC/NB stay flat?
from scipy.stats import spearmanr
lad = out[out.calibrate != "none"]
print("\nSpearman(flexibility, ECE_recovery) =", round(spearmanr(lad.flexibility, lad.ece_recovery).statistic, 3))
print("mean |AURC_recovery| across rungs =", round(lad.aurc_recovery.abs().mean(), 4),
      "| mean |NB_recovery| =", round(lad.nb_recovery.abs().mean(), 4))
verdict = ("ECE recovery rises with flexibility while AURC/NB recovery ~0 -> NOT a flexibility limitation, airtight"
           if spearmanr(lad.flexibility, lad.ece_recovery).statistic > 0.5 and lad.aurc_recovery.abs().max() < 0.01
           else "pattern broken -> report as-is")
print("VERDICT:", verdict)
json.dump({"ladder": rows, "verdict": verdict}, open(f"{R}/p2_summary.json", "w"), indent=2)
print("\nWROTE p2_flexibility_ladder.csv + p2_summary.json")
