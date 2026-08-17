"""Is the net-benefit axis measured where a model is needed?

Decision-curve analysis is interpretable only against the default strategies. Section 4.6 reports
the mean net benefit over the configured threshold range and compares reduced against full models,
but never against treating everyone -- the default that binds at high prevalence. Where the whole
evaluated range lies below the prevalence, treat-all is strong throughout it, and a change in a
model's net benefit there is a change in a quantity no clinician would act on.

This arm computes, for every dataset and budget, the net benefit of treat-all over the identical
threshold grid, and reports three things:

  1. whether the configured range contains the prevalence at all;
  2. how far each model sits above or below treat-all;
  3. how many of the materially-degraded net-benefit cells the study counts come from datasets
     where the axis is uninformative -- which is what decides whether the headline count is
     sensitive to the finding or robust to it.

Prevalence is read from committed results rather than recomputed from raw data, so this arm runs
from a clone with no datasets on disk: the cross-dataset correlates table carries it for all twelve,
and is located by filename under results/ so this script is identical in the working repository and
in the released compendium, which shelve it differently. That table's readmission figure is the
n=6000 subsample, so the readmission prevalence is taken from the committed full-cohort out-of-fold
cache instead, which is the cohort the study analyses.

Committed-results-only. No model is fitted and no outcome is redefined; treat-all is a closed form
in the prevalence and the threshold.

    PYTHONPATH=src python experiments/enrichments/compute_net_benefit_defaults.py
"""
from __future__ import annotations

import json
import os as _os

# Repo root resolved from this file rather than hard-coded. Override with NSCLINFS_REPO.
_REPO_ROOT = _os.environ.get("NSCLINFS_REPO") or _os.path.dirname(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, _os.path.join(_REPO_ROOT, "src"))
from nsclinfs.metrics import mean_net_benefit_treat_all  # noqa: E402

ROOT = Path(_REPO_ROOT)
OUT = ROOT / "results" / "enrichments" / "21_net_benefit_default_strategies"


# The cross-dataset correlates table is shelved under different directory names in the working
# repository and in the released compendium, so it is located by filename rather than by path. That
# keeps this script identical in both trees -- as scripts/provenance_map.py already is for the column
# manifest -- without either tree's directory layout being written into the other's.
CORRELATES_FILE = "tier8_correlates_clinical.csv"


def prevalences() -> tuple[dict[str, float], str]:
    """Per-dataset outcome prevalence, from committed results only."""
    found = sorted((ROOT / "results").rglob(CORRELATES_FILE))
    if not found:
        raise SystemExit(f"no {CORRELATES_FILE} anywhere under results/")
    t8 = pd.read_csv(found[0])
    prev = {r.dataset: float(r.prevalence) for r in t8.itertuples()}

    # The readmission cohort is analysed in full, so its prevalence comes from the full-cohort
    # cache rather than from tier8's n=6000 subsample row.
    caches = sorted((ROOT / "results/cache/poof").glob("diabetes130__*__rep0.parquet"))
    note = f"cross-dataset correlates table ({CORRELATES_FILE})"
    if caches:
        d = pd.read_parquet(caches[0], columns=["y"])
        prev["diabetes130"] = float(d["y"].mean())
        note += f"; diabetes130 from the full-cohort cache (n={len(d)})"
    return prev, note


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    calib = json.loads((ROOT / "config" / "calibration.json").read_text(encoding="utf-8"))
    grid = calib["metric_params"]["net_benefit"]
    t_lo, t_hi, n_t = float(grid["t_lo"]), float(grid["t_hi"]), int(grid["n_thresholds"])

    prev, prev_note = prevalences()
    summary = pd.read_csv(ROOT / "results" / "summary.csv", comment="#")
    nb = summary[summary.outcome == "net_benefit"].copy()

    rows = []
    for (ds, bt, budget), g in nb.groupby(["dataset", "budget_type", "budget"], dropna=False):
        if ds not in prev:
            continue
        pv = prev[ds]
        treat_all = mean_net_benefit_treat_all(pv, t_lo, t_hi, n_t)
        model = float(g["mean"].mean())
        rows.append({
            "dataset": ds,
            "prevalence": round(pv, 4),
            "budget_type": bt,
            "budget": budget,
            "n_cells": int(len(g)),
            "mean_net_benefit_model": round(model, 4),
            "mean_net_benefit_treat_all": round(treat_all, 4),
            "model_minus_treat_all": round(model - treat_all, 4),
            "beats_treat_all": bool(model > treat_all),
            "range_contains_prevalence": bool(t_lo <= pv <= t_hi),
        })

    df = pd.DataFrame(rows).sort_values(["dataset", "budget_type", "budget"])
    df.to_csv(OUT / "net_benefit_vs_treat_all.csv", index=False, lineterminator="\n")

    full = df[(df.budget_type == "frac") & (df.budget == "frac:1")].sort_values(
        "model_minus_treat_all")
    uninformative = sorted(full[~full.range_contains_prevalence].dataset)
    never_beats = sorted(df[~df.beats_treat_all].dataset.unique())

    print(f"threshold grid: {n_t} points on [{t_lo}, {t_hi}]   (from config/calibration.json)")
    print(f"prevalence source: {prev_note}\n")
    print(f"  {'dataset':<15}{'prev':>7}{'NB model':>10}{'treat-all':>11}{'difference':>12}")
    for r in full.itertuples():
        flag = "" if r.beats_treat_all else "   <-- below treat-all"
        print(f"  {r.dataset:<15}{r.prevalence:>7.3f}{r.mean_net_benefit_model:>10.4f}"
              f"{r.mean_net_benefit_treat_all:>11.4f}{r.model_minus_treat_all:>12.4f}{flag}")

    # How much of the headline net-benefit count rests on the uninformative datasets. If the count
    # barely moves, the finding is a scope disclosure; if it moves a lot, it is a correction.
    material = summary[(summary.outcome == "net_benefit") & (summary.budget_type == "frac")
                       & (summary.frac == 0.25) & (summary.calibrate == "none")]
    worse_col = "material_worse" if "material_worse" in material.columns else "material"
    total = int(material[worse_col].astype(bool).sum())
    from_uninformative = int(
        material[material.dataset.isin(uninformative)][worse_col].astype(bool).sum())

    meta = {
        "STATUS": "validated",
        "threshold_grid": {"t_lo": t_lo, "t_hi": t_hi, "n_thresholds": n_t},
        "prevalence_source": prev_note,
        "datasets_whose_range_excludes_prevalence": uninformative,
        "datasets_never_beating_treat_all": never_beats,
        "n_datasets": int(full.dataset.nunique()),
        "n_beating_treat_all_at_full_budget": int(full.beats_treat_all.sum()),
        "smallest_margin_over_treat_all": {
            "dataset": str(full[full.beats_treat_all].iloc[0].dataset),
            "margin": float(full[full.beats_treat_all].iloc[0].model_minus_treat_all),
        },
        "material_net_benefit_cells_at_25pct": total,
        "material_cells_from_uninformative_datasets": from_uninformative,
        "material_cells_retained": total - from_uninformative,
    }
    (OUT / "net_benefit_default_strategies.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"\n  range excludes the prevalence on: {', '.join(uninformative) or 'none'}")
    print(f"  never beats treat-all at any budget: {', '.join(never_beats) or 'none'}")
    print(f"  {meta['n_beating_treat_all_at_full_budget']} of {meta['n_datasets']} datasets beat "
          f"treat-all at the full budget; smallest margin "
          f"{meta['smallest_margin_over_treat_all']['margin']:+.4f} on "
          f"{meta['smallest_margin_over_treat_all']['dataset']}")
    print(f"\n  materially-degraded net-benefit cells at the 25 % budget: {total}; "
          f"{from_uninformative} of them on {', '.join(uninformative)}, "
          f"leaving {total - from_uninformative}")
    print(f"\nwrote {OUT}/net_benefit_vs_treat_all.csv and net_benefit_default_strategies.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
