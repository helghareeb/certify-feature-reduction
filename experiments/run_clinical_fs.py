"""Run the feature-reduction calibration/fairness audit and emit the single canonical
summary CSV (R2). Every reduction level is compared, paired across reps, to the
full-feature baseline (reference_frac), Holm-corrected within each
(dataset, method, classifier, outcome) family with a 5000-bootstrap CI on the
paired difference.

    PYTHONPATH=src python experiments/run_clinical_fs.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from nsclinfs import data as dataload
from nsclinfs.hashing import CALIB_HASH_KEY, assert_single_hash, content_hash
from nsclinfs.run import run_grid
from nsclinfs.stats import bootstrap_diff_ci, cohens_d_paired, holm, mean_ci, paired_wilcoxon

KEYS = ["dataset", "method", "classifier", "calibrate"]
REF_BUDGET = "frac:1"  # the full-feature reference level

# Outcomes where a HIGHER value is better; for all others (ece, brier, aurc, the gaps)
# a higher value is worse. Used to resolve a two-sided "material" difference into the
# direction that actually matters: material_worse (degraded) vs material_better (improved).
HIGHER_BETTER = {"auroc", "accuracy", "net_benefit"}


def aggregate(raw: pd.DataFrame, outcomes: list[str], ref: float, alpha: float, seed: int) -> pd.DataFrame:
    """One row per (cell, budget, outcome), paired against the full-feature reference.

    v2: budgets pivot on the `budget` label ("frac:0.25" / "k:2"); Holm multiplicity
    families are computed WITHIN each budget_type, so adding the exact-k arm cannot move
    the p_holm of the fractional comparisons the submitted paper reported. A raw file
    from the v1 schema (no `budget` column) is upgraded in place from `frac`.
    """
    raw = raw.copy()
    if "budget" not in raw.columns:                      # v1 raw compatibility
        raw["budget_type"] = "frac"
        raw["budget"] = "frac:" + raw["frac"].map("{:g}".format)
    kmap = (raw.drop_duplicates(subset=KEYS[:1] + ["budget"])
                .set_index(["dataset", "budget"])[["k_features", "n_features"]]
            if "k_features" in raw.columns else None)
    ref_label = f"frac:{ref:g}"
    rows = []
    for (ds, method, clf, calibrate), g in raw.groupby(KEYS):
        for outcome in outcomes:
            piv = g.pivot_table(index="rep", columns="budget", values=outcome)
            if ref_label not in piv.columns:
                continue
            btype_of = g.drop_duplicates("budget").set_index("budget")["budget_type"].to_dict()
            fams: dict[str, list] = {}
            for budget in sorted(piv.columns):
                vals = piv[budget].dropna().to_numpy()
                lo, hi = mean_ci(vals, seed=seed)
                row = {"dataset": ds, "method": method, "classifier": clf, "calibrate": calibrate,
                       "budget": budget, "budget_type": btype_of.get(budget, "frac"),
                       "frac": float(budget.split(":")[1]) if budget.startswith("frac:") else np.nan,
                       "outcome": outcome, "mean": float(np.mean(vals)), "ci_lo": lo, "ci_hi": hi,
                       "n": int(len(vals)), "delta": np.nan, "cohens_d": np.nan,
                       "diff_ci_lo": np.nan, "diff_ci_hi": np.nan, "p_raw": np.nan,
                       "p_holm": np.nan, "material": False,
                       "material_worse": False, "material_better": False}
                if kmap is not None and (ds, budget) in kmap.index:
                    row["k_features"] = int(kmap.loc[(ds, budget), "k_features"])
                    row["n_features"] = int(kmap.loc[(ds, budget), "n_features"])
                if budget != ref_label:
                    paired = piv[[budget, ref_label]].dropna()
                    a, b = paired[budget].to_numpy(), paired[ref_label].to_numpy()
                    dlo, dhi = bootstrap_diff_ci(a, b, seed=seed)
                    row.update(delta=float(np.mean(a - b)), cohens_d=cohens_d_paired(a, b),
                               diff_ci_lo=dlo, diff_ci_hi=dhi, p_raw=paired_wilcoxon(a, b))
                    fams.setdefault(row["budget_type"], []).append(row)
                rows.append(row)
            for fam in fams.values():                    # Holm within budget_type (see docstring)
                ph = holm([r["p_raw"] for r in fam])
                worse_when_positive = outcome not in HIGHER_BETTER
                for r, p in zip(fam, ph):
                    r["p_holm"] = float(p)
                    r["material"] = bool(p < alpha and (r["diff_ci_lo"] > 0 or r["diff_ci_hi"] < 0))
                    is_worse = (r["delta"] > 0) if worse_when_positive else (r["delta"] < 0)
                    r["material_worse"] = bool(r["material"] and is_worse)
                    r["material_better"] = bool(r["material"] and not is_worse)
    return pd.DataFrame(rows)


def run_chunk(calib: dict, data_dir: str, raw_csv: str, rep_start: int, rep_end: int, append: bool,
              only: dict | None = None) -> int:
    """Run (a shard of) the grid. `only` optionally restricts {datasets, methods, classifiers,
    calibrations} for parallel sharding; the shard carries the FULL config hash either way."""
    chash = content_hash(calib)
    only = only or {}
    calibrations = only.get("calibrations") or calib.get("calibrations", ["none"])
    budgets = calib.get("budgets")                     # v2 form; v1 configs carry "fracs"
    dataset_params = calib.get("dataset_params", {})
    frames, nb_rows = [], []
    for ds in (only.get("datasets") or calib["datasets"]):
        X, y, sensitive = dataload.load(ds, params=dataset_params.get(ds))
        g = run_grid(X, y, sensitive,
                     fracs=None if budgets else calib["fracs"], budgets=budgets,
                     methods=(only.get("methods") or calib["reduction_methods"]),
                     classifiers=(only.get("classifiers") or calib["classifiers"]),
                     n_reps=int(calib["REPS"]), master_seed=calib["RANDOM_SEED"],
                     n_folds=int(calib["n_folds"]), dataset=ds,
                     rep_start=rep_start, rep_end=rep_end, calibrations=calibrations,
                     metric_params=calib.get("metric_params"), persist=calib.get("persist"))
        nb_rows += g.attrs.get("nb_curves", [])
        frames.append(g)
    raw = pd.concat(frames, ignore_index=True)
    raw[CALIB_HASH_KEY] = chash
    Path(raw_csv).parent.mkdir(parents=True, exist_ok=True)
    if append and Path(raw_csv).exists():
        prev = pd.read_csv(raw_csv)
        assert_single_hash(list(prev.get(CALIB_HASH_KEY, [])) + [chash])   # refuse cross-hash merges
        raw = (pd.concat([prev, raw], ignore_index=True)
               .drop_duplicates(subset=["dataset", "method", "classifier", "calibrate", "budget", "rep"]
                                if "budget" in raw.columns else
                                ["dataset", "method", "classifier", "calibrate", "frac", "rep"],
                                keep="last"))
    tmp = Path(raw_csv).with_suffix(".tmp")
    raw.to_csv(tmp, index=False)
    tmp.replace(raw_csv)                                # atomic: a killed run never half-writes
    if nb_rows:
        nb_path = Path(raw_csv).with_name(Path(raw_csv).stem + "_nb_curves.parquet")
        nb = pd.DataFrame(nb_rows)
        nb[CALIB_HASH_KEY] = chash
        nb.to_parquet(nb_path, index=False)
    print(f"[clinical-fs] ran reps [{rep_start},{rep_end}); raw now {len(raw)} rows -> {raw_csv}")
    return len(raw)


def do_aggregate(calib: dict, raw_csv: str, out_csv: str) -> dict:
    chash = content_hash(calib)
    reps = int(calib["REPS"])
    raw = pd.read_csv(raw_csv)
    # R6, enforced not implied: the raw rows must all carry exactly the hash of THIS config.
    raw_hash = assert_single_hash(raw.get(CALIB_HASH_KEY, pd.Series(dtype=str)))
    if raw_hash != chash:
        raise SystemExit(f"raw {raw_csv} was produced under calibration {raw_hash[:12]}…, "
                         f"but --calib hashes to {chash[:12]}… — refusing to aggregate across configs")
    summary = aggregate(raw, calib["outcomes"], float(calib["reference_frac"]),
                        float(calib["stat_alpha"]), int(calib["RANDOM_SEED"]))
    summary[CALIB_HASH_KEY] = chash
    status = "validated" if reps >= 30 else "provisional"
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        f.write(f"# STATUS: {status}  (REPS={reps})\n")
        f.write(f"# calibration_sha256: {chash}\n")   # canonical R6 header (audit-gate pattern)
        f.write(f"# {CALIB_HASH_KEY}: {chash}\n")
        f.write("# calibration (ECE/Brier) and subgroup gaps vs full-feature baseline; "
                "Holm-corrected within (dataset,method,classifier,outcome); 5000-bootstrap paired-diff CI\n")
        summary.to_csv(f, index=False)

    # headline: at the most aggressive FRACTIONAL budget, which outcomes degrade materially
    # (mean over method/classifier)? The exact-k arm never enters the headline family.
    fracs = (calib.get("budgets") or {}).get("fracs") or calib["fracs"]
    aggr = summary[summary["frac"] == min(fracs)]
    if "budget_type" in aggr.columns:
        aggr = aggr[aggr["budget_type"] == "frac"]
    if "calibrate" in aggr.columns:                    # main finding = uncalibrated (raw) probabilities
        aggr = aggr[aggr["calibrate"] == "none"]
    head = {}
    for outcome in ["auroc", "ece", "brier", "aurc", "auroc_gap", "ece_gap"]:
        sub = aggr[aggr["outcome"] == outcome]
        head[outcome] = {"mean_delta_vs_full": round(float(sub["delta"].mean()), 4),
                         "n_material_worse": int(sub["material_worse"].sum()),
                         "n_material_better": int(sub["material_better"].sum()),
                         "n_material_cells": int(sub["material"].sum()), "n_cells": int(len(sub))}
    out = {"status": status, "reps": reps, "n_datasets": int(raw["dataset"].nunique()),
           "most_aggressive_frac": min(fracs), "headline_by_outcome": head, "calib_sha256": chash}
    Path(out_csv).with_suffix(".headline.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"[clinical-fs] STATUS={status} REPS={reps}; at frac={min(fracs)} vs full features "
          f"(worse / better / two-sided-material of {len(aggr[aggr['outcome']=='auroc'])}):")
    for o, h in head.items():
        print(f"  {o:<10} mean delta {h['mean_delta_vs_full']:+.4f}  "
              f"worse {h['n_material_worse']}  better {h['n_material_better']}  (material {h['n_material_cells']})")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Feature-reduction calibration/fairness audit")
    p.add_argument("--calib", default="config/calibration.json")
    p.add_argument("--data-dir", default="data/cleveland")
    p.add_argument("--out", default="results/summary.csv")
    p.add_argument("--raw", default="results/raw/audit.csv")
    p.add_argument("--rep-start", type=int, default=0)
    p.add_argument("--rep-end", type=int, default=None, help="exclusive; default = REPS")
    p.add_argument("--append", action="store_true", help="merge this chunk into existing raw")
    p.add_argument("--aggregate-only", action="store_true")
    p.add_argument("--datasets", nargs="*", default=None, help="shard filter (full config hash still applies)")
    p.add_argument("--methods", nargs="*", default=None)
    p.add_argument("--classifiers", nargs="*", default=None)
    p.add_argument("--calibrations", nargs="*", default=None)
    a = p.parse_args()
    calib = json.loads(Path(a.calib).read_text())
    reps = int(calib["REPS"])
    if a.aggregate_only:
        do_aggregate(calib, a.raw, a.out)
        return 0
    only = {k: getattr(a, k) for k in ("datasets", "methods", "classifiers", "calibrations")
            if getattr(a, k)}
    rep_end = reps if a.rep_end is None else a.rep_end
    run_chunk(calib, a.data_dir, a.raw, a.rep_start, rep_end, a.append, only=only)
    if rep_end >= reps and not only:
        do_aggregate(calib, a.raw, a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
