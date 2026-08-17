"""Dataset-level inference, and the effect-size distribution behind the cell counts.

Two things the manuscript's headline counts do not carry, both computable from the released
per-configuration summary and neither requiring a new fit.

**1. Inference at the level where the units are independent.** The per-cell verdicts come from a
Wilcoxon signed-rank test over 30 repetitions, and those repetitions are re-splits of one cohort
rather than independent samples, so their spread understates the uncertainty of the mean and the
test grows more confident with repetition count alone. The twelve datasets, by contrast, are
independent of one another. Collapsing each dataset to its mean paired difference across rankers
and learners and testing the resulting twelve values -- by an exact sign test, which assumes only
independence and a continuous distribution -- gives a claim that does not depend on how many times
a cohort was re-split. This is the conservative counterpart to the cell counts, not a replacement:
it has twelve observations, so it can only speak to direction.

**2. The distribution of effect sizes behind each count.** "Material" is a significance verdict
with no minimum magnitude, so a count of material cells says nothing about how large the effects
in it are. For each budget and outcome this reports the median and interquartile range of the
per-cell paired difference, and how many cells clear a stated magnitude, so a reader can see the
counts and the sizes together.

    PYTHONPATH=src python experiments/enrichments/compute_dataset_level_inference.py
"""
from __future__ import annotations

import json
import os as _os

# Repo root resolved from this file rather than hard-coded. Override with NSCLINFS_REPO.
_REPO_ROOT = _os.environ.get("NSCLINFS_REPO") or _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(_REPO_ROOT)
OUT = ROOT / "results" / "enrichments" / "19_dataset_level_inference"

# Sign of a degrading change, per outcome.
WORSE_IF = {"aurc": +1, "ece": +1, "brier": +1, "conformal_efficiency": +1,
            "selective_ece": +1, "auroc": -1, "net_benefit": -1}
# Magnitudes reported alongside the counts. Not thresholds the paper adopts -- reference points
# so that "material" can be read against a size rather than only against a p-value.
MAGNITUDES = {"aurc": 0.01, "ece": 0.01, "brier": 0.01, "auroc": 0.01,
              "net_benefit": 0.005, "conformal_efficiency": 0.05, "selective_ece": 0.01}
OUTCOMES = list(WORSE_IF)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(ROOT / "results/summary.csv", comment="#")
    d = d[(d.budget_type == "frac") & (d.calibrate == "none") & (d.frac < 1.0)]

    sign_rows, size_rows = [], []
    for frac in sorted(d.frac.unique(), reverse=True):
        for oc in OUTCOMES:
            s = d[(d.frac == frac) & (d.outcome == oc)]
            if s.empty:
                continue
            worse = WORSE_IF[oc]

            # --- 2. effect-size distribution over the cells -------------------------
            delta = s.delta.dropna()
            # oriented so that positive always means "reduction is worse"
            oriented = delta * worse
            mag = MAGNITUDES[oc]
            size_rows.append({
                "frac": frac, "outcome": oc, "n_cells": int(len(oriented)),
                "median_worse_oriented": round(float(oriented.median()), 5),
                "q25": round(float(oriented.quantile(0.25)), 5),
                "q75": round(float(oriented.quantile(0.75)), 5),
                "n_material_worse": int(s.material_worse.sum()),
                "magnitude_ref": mag,
                "n_worse_beyond_magnitude": int((oriented >= mag).sum()),
                "n_material_worse_beyond_magnitude": int(
                    ((oriented >= mag) & (s.material_worse == 1)).sum()),
            })

            # --- 1. dataset-level sign test ----------------------------------------
            per_ds = s.groupby("dataset").delta.mean() * worse
            n_pos = int((per_ds > 0).sum())
            n_neg = int((per_ds < 0).sum())
            n_eff = n_pos + n_neg
            p = float(stats.binomtest(n_pos, n_eff, 0.5, alternative="greater").pvalue) \
                if n_eff else float("nan")
            sign_rows.append({
                "frac": frac, "outcome": oc, "n_datasets": int(per_ds.size),
                "n_datasets_worse": n_pos, "n_datasets_better": n_neg,
                "median_across_datasets": round(float(per_ds.median()), 5),
                "sign_test_p_one_sided": round(p, 6),
                "sign_test_significant_05": bool(p < 0.05),
            })

    sign = pd.DataFrame(sign_rows)
    size = pd.DataFrame(size_rows)
    sign.to_csv(OUT / "dataset_level_sign_test.csv", index=False, lineterminator="\n")
    size.to_csv(OUT / "effect_size_distribution.csv", index=False, lineterminator="\n")

    head = {}
    for oc in OUTCOMES:
        r = sign[(sign.frac == 0.25) & (sign.outcome == oc)]
        z = size[(size.frac == 0.25) & (size.outcome == oc)]
        if r.empty:
            continue
        head[oc] = {
            "datasets_worse_of": f"{int(r.n_datasets_worse.iloc[0])}/{int(r.n_datasets.iloc[0])}",
            "sign_test_p": float(r.sign_test_p_one_sided.iloc[0]),
            "median_effect": float(z.median_worse_oriented.iloc[0]),
            "iqr": [float(z.q25.iloc[0]), float(z.q75.iloc[0])],
            "material_worse_cells": int(z.n_material_worse.iloc[0]),
            "cells_beyond_ref_magnitude": int(z.n_worse_beyond_magnitude.iloc[0]),
            "ref_magnitude": float(z.magnitude_ref.iloc[0]),
        }
    (OUT / "dataset_level_inference.json").write_text(
        json.dumps(head, indent=2) + "\n", encoding="utf-8", newline="\n")

    print("At the 25% budget, by outcome:")
    print(f"  {'outcome':<22}{'datasets worse':>15}{'sign p':>10}"
          f"{'median':>10}{'material':>10}{'>=ref':>8}")
    for oc, v in head.items():
        print(f"  {oc:<22}{v['datasets_worse_of']:>15}{v['sign_test_p']:>10.4f}"
              f"{v['median_effect']:>10.4f}{v['material_worse_cells']:>10}"
              f"{v['cells_beyond_ref_magnitude']:>8}")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
