"""R1.1 reanalysis: is the cross-dataset screen driven by feature count p, or by the
ABSOLUTE number of retained features k?

The budget rule k = max(1, round(frac*p)) mechanically links k to p at every fractional
budget, so the published Spearman rho(p, harm) = -0.73 cannot by itself distinguish
"datasets with more candidate features are safer to reduce" from "reducing to one or two
features is unsafe" (Reviewer 1, point 1). This script separates the explanations with
the data already in the canonical summary — no new model fits:

  1. the retained-k table per dataset x budget (the rule's consequences, incl. the floor);
  2. rho of harm against p, k_min, and log2(k_min), plus the k=1-collapse indicator;
  3. rho(p, harm) EXCLUDING the two floor-collapsed datasets (haberman, mammographic);
  4. cross-dataset comparisons at matched absolute k, using every budget level: the same
     k value reached by different datasets at different fracs carries the same paired
     delta-vs-full-features interpretation.

Emits results/meta_k.json + paper/meta_k_table.tex. Reads ONLY the canonical summary
(R2) + dataset p from the loaders. Definitive resolution comes from the v2 exact-k arm;
this analysis is what the response letter's R1.1 numbers are drafted from.

    PYTHONPATH=src python experiments/meta_analysis_k.py [--summary results/summary.csv]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from nsclinfs import data as dataload
from nsclinfs.hashing import CALIB_HASH_KEY, assert_single_hash
from nsclinfs.reduction import retained_k

FLOOR_DATASETS = ("haberman", "mammographic")  # collapse to k=1 inside the frac grid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="results/summary.csv")
    ap.add_argument("--outcome", default="aurc")
    a = ap.parse_args()

    s = pd.read_csv(a.summary, comment="#")
    # R6: use the shared guard, not a local re-implementation. The hand-rolled version
    # this replaces tested only len(hashes) > 1, so a summary carrying NO calibration
    # stamp at all passed it silently -- and an absent stamp is exactly as bad as a
    # conflicting one. assert_single_hash raises on both.
    assert_single_hash(s[CALIB_HASH_KEY] if CALIB_HASH_KEY in s.columns else [])
    fracs = sorted(s.loc[s["frac"].notna(), "frac"].unique())   # exact-k rows carry NaN frac
    frac_min = min(fracs)

    p_of = {ds: dataload.load(ds)[0].shape[1] for ds in sorted(s["dataset"].unique())}

    # -- 1. the retained-k table ------------------------------------------------------
    ktab = {ds: {f: retained_k(f, p) for f in fracs} for ds, p in p_of.items()}

    # -- harm at the most aggressive budget (same definition as meta_analysis.py) -----
    at = s[(s["frac"] == frac_min) & (s["outcome"] == a.outcome)]
    harm = at.groupby("dataset")["delta"].mean()
    df = pd.DataFrame({"dataset": harm.index, "harm": harm.values})
    df["p"] = df["dataset"].map(p_of)
    df["k_min"] = df.apply(lambda r: retained_k(frac_min, r["p"]), axis=1)
    df["hits_k1"] = df["dataset"].apply(lambda d: min(ktab[d].values()) == 1)
    df = df.sort_values("harm", ascending=False).reset_index(drop=True)

    # -- 2/3. correlations ------------------------------------------------------------
    def rho(x, y):
        r, pv = spearmanr(x, y)
        return {"rho": round(float(r), 3), "p": round(float(pv), 4)}

    corr = {
        "p_vs_harm": rho(df["p"], df["harm"]),
        "k_min_vs_harm": rho(df["k_min"], df["harm"]),
        "log2_k_min_vs_harm": rho(np.log2(df["k_min"]), df["harm"]),
        "hits_k1_vs_harm": rho(df["hits_k1"].astype(int), df["harm"]),
    }
    sub = df[~df["dataset"].isin(FLOOR_DATASETS)]
    corr["p_vs_harm_excl_floor"] = rho(sub["p"], sub["harm"])
    corr["n_excl_floor"] = int(len(sub))

    # -- Enrichment #2: robustness of the screen -------------------------------------
    # (a) leave-one-dataset-out: does any single dataset carry the correlation?
    # (b) seeded 5000-resample bootstrap over datasets -> percentile CI on rho.
    robustness = {}
    for xcol, label in (("p", "p_vs_harm"), ("k_min", "k_min_vs_harm")):
        lodo = {}
        for ds in df["dataset"]:
            d = df[df["dataset"] != ds]
            r, _ = spearmanr(d[xcol], d["harm"])
            lodo[ds] = round(float(r), 3)
        rng = np.random.default_rng(20260626)
        boots = []
        idx = np.arange(len(df))
        for _ in range(5000):
            take = rng.choice(idx, size=len(idx), replace=True)
            x, h = df[xcol].to_numpy()[take], df["harm"].to_numpy()[take]
            if len(np.unique(x)) > 1 and len(np.unique(h)) > 1:
                r, _ = spearmanr(x, h)
                if np.isfinite(r):
                    boots.append(r)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        robustness[label] = {
            "lodo": lodo,
            "lodo_range": [round(min(lodo.values()), 3), round(max(lodo.values()), 3)],
            "lodo_all_negative": all(v < 0 for v in lodo.values()),
            "bootstrap_ci95": [round(float(lo), 3), round(float(hi), 3)],
            "bootstrap_n_valid": len(boots),
        }
    corr["robustness"] = robustness

    # -- 4. matched absolute k across datasets, all budget levels ---------------------
    # v2 summaries carry k_features and BOTH budget arms (the exact-k arm puts k=1,2,4,8
    # on every dataset -- the decisive matched comparison); v1 summaries fall back to
    # deriving k from frac.
    lv = s[(s["outcome"] == a.outcome) & (s["delta"].notna())].copy()
    if "k_features" in lv.columns:
        lv["k"] = lv["k_features"].astype(int)
    else:
        lv["k"] = lv.apply(lambda r: retained_k(r["frac"], p_of[r["dataset"]]), axis=1)
    cell = (lv.groupby(["dataset", "k"], as_index=False)["delta"].mean()
              .assign(p=lambda t: t["dataset"].map(p_of)))
    matched = {int(k): {r["dataset"]: round(float(r["delta"]), 4) for _, r in g.iterrows()}
               for k, g in cell.groupby("k") if len(g) >= 2}

    # -- 5. the decisive exact-k readout: harm at k=1 for EVERY dataset ---------------
    exact_k1 = {}
    if "budget" in s.columns:
        k1 = s[(s["budget"] == "k:1") & (s["outcome"] == a.outcome)]
        exact_k1 = {ds: round(float(g["delta"].mean()), 4) for ds, g in k1.groupby("dataset")}

    out = {
        "outcome": a.outcome, "frac_min": frac_min,
        "retained_k_table": {ds: {str(f): k for f, k in row.items()} for ds, row in ktab.items()},
        "harm_by_dataset": {r["dataset"]: {"harm": round(float(r["harm"]), 4), "p": int(r["p"]),
                                            "k_min": int(r["k_min"]), "hits_k1": bool(r["hits_k1"])}
                            for _, r in df.iterrows()},
        "correlations": corr,
        "matched_k_harm": matched,
        "exact_k1_harm": exact_k1,
        "note": "k derives deterministically from (frac, p) via reduction.retained_k -- "
                "identical to the k_features the runner logs per raw row.",
    }
    Path("results/meta_k.json").write_text(json.dumps(out, indent=2) + "\n")

    # -- table fragment for the manuscript --------------------------------------------
    lines = ["% auto-generated by experiments/meta_analysis_k.py from " + a.summary,
             r"\begin{tabular}{@{}lrrrrc@{}}", r"\toprule",
             r"Dataset & $p$ & $k$@25\,\% & harm & $\rho$-rank & floor? \\", r"\midrule"]
    for i, r in df.iterrows():
        lines.append(f"{r['dataset']} & {int(r['p'])} & {int(r['k_min'])} & "
                     f"{r['harm']:+.3f} & {i + 1} & " + (r"\checkmark" if r["hits_k1"] else "--") + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    Path("paper/meta_k_table.tex").write_text("\n".join(lines) + "\n")

    print(json.dumps({"correlations": corr, "matched_k_harm": matched}, indent=2))
    print("\nharm ranking (most harmed first):")
    print(df.to_string(index=False, float_format=lambda v: f"{v:+.4f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
