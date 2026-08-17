"""Decision-flip decomposition: which way the flips go, and how that depends on the threshold.

Section 4.11 counts the patients whose treatment decision a reduced model changes, and reports
one direction of that change -- the true cases moved out of treatment. A flip has two directions,
and at the pre-registered operating point the other one is the larger. This arm reports the full
decomposition, and sweeps the threshold to show that the sign of the harm depends on where the
threshold sits relative to the reduced model's predicted-risk distribution.

Three quantities per (cell, threshold):

  1. the 2x2 decomposition of the majority-flipped patients: direction (newly recommended vs
     withdrawn) x true outcome (positive vs negative);
  2. the treated fraction under each model, and the percentiles of each model's predicted risk,
     which is what makes the direction predictable rather than surprising;
  3. the paired net-benefit difference at that threshold, which the decomposition should
     reproduce, since NB(t) = TP/n - (FP/n) * t/(1-t) is linear in the two counts.

The pre-registered threshold and cell come from config/analysis.json and are unchanged. The
threshold sweep is post-hoc and is labelled as such wherever it is reported: it is a sensitivity
analysis of a fixed measurement, not a search for an operating point.

Cache-only. No model is fitted and no number is computed that is not already implied by the
committed out-of-fold predictions.

    PYTHONPATH=src python experiments/enrichments/compute_flip_decomposition.py
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
from nsclinfs.hashing import CALIB_HASH_KEY, assert_single_hash  # noqa: E402

ROOT = Path(_REPO_ROOT)
OUT = ROOT / "results" / "enrichments" / "18_decision_flip_decomposition"

# The pre-registered operating point comes first in every table; the rest are the sweep.
SWEEP = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60]
PCTL = [0.10, 0.25, 0.50, 0.75, 0.90]


def load_poof(dataset: str, cell: dict) -> pd.DataFrame:
    name = "__".join([dataset, cell["method"], cell["classifier"], cell["calibrate"]])
    files = sorted((ROOT / "results/cache/poof").glob(f"{name}__rep*.parquet"))
    if not files:
        raise SystemExit(f"no out-of-fold cache for {name}")
    reps = []
    for f in files:
        d = pd.read_parquet(f)
        d["rep"] = int(f.stem.rsplit("rep", 1)[1])
        reps.append(d)
    df = pd.concat(reps)
    if CALIB_HASH_KEY in df.columns:
        assert_single_hash(df[CALIB_HASH_KEY])
    return df.reset_index(names="patient")


def decompose(d: pd.DataFrame, full: str, red: str, t: float) -> dict:
    """One row of the decomposition, at threshold t.

    A patient's flip is defined per repetition and then majority-voted, so the direction has to
    be defined the same way: a majority-flipped patient is classed by whichever direction it
    takes in more of its flipping repetitions. Defining direction instead from the mean
    probabilities -- which is what the original worked-example script did for its single
    withdrawn-treatment count -- leaves the two directions failing to sum to the flip count,
    because a patient can flip in most repetitions while its mean probabilities sit on the same
    side of the threshold. Both are computed here and the mean-probability figures are kept under
    a `_meanp` suffix so the published number can be checked against its own definition.
    """
    w = t / (1.0 - t)
    x = d.copy()
    x["treat_full"] = x[full] >= t
    x["treat_red"] = x[red] >= t
    x["gained"] = (~x["treat_full"]) & x["treat_red"]     # reduction newly recommends
    x["lost"] = x["treat_full"] & (~x["treat_red"])       # reduction withdraws
    x["flip"] = x["gained"] | x["lost"]

    g = x.groupby("patient").agg(
        y=("y", "first"),
        flip_rate=("flip", "mean"), gain_rate=("gained", "mean"), lose_rate=("lost", "mean"),
        p_full=(full, "mean"), p_red=(red, "mean"))
    maj = g[g.flip_rate >= 0.5]

    def split(sub):
        gained = int((sub.gain_rate > sub.lose_rate).sum())
        lost = int((sub.lose_rate > sub.gain_rate).sum())
        tied = int(len(sub) - gained - lost)
        return gained, lost, tied

    pos_gained, pos_lost, pos_tied = split(maj[maj.y == 1])
    neg_gained, neg_lost, neg_tied = split(maj[maj.y == 0])

    # The original definition, retained so the published figure can be reconciled.
    pos_lost_meanp = int(((maj.y == 1) & (maj.p_full >= t) & (maj.p_red < t)).sum())
    pos_gained_meanp = int(((maj.y == 1) & (maj.p_full < t) & (maj.p_red >= t)).sum())

    # Net benefit per repetition, then paired across repetitions.
    nb = {}
    for lab, col in (("full", full), ("red", red)):
        vals = []
        for _, gr in x.groupby("rep"):
            n = len(gr)
            treat = gr[col] >= t
            tp = int((treat & (gr.y == 1)).sum())
            fp = int((treat & (gr.y == 0)).sum())
            vals.append(tp / n - (fp / n) * w)
        nb[lab] = pd.Series(vals)
    d_nb = float((nb["red"] - nb["full"]).mean())

    # What the decomposition alone implies for the net-benefit change.
    n_pat = int(len(g))
    d_nb_pred = ((pos_gained - pos_lost) - w * (neg_gained - neg_lost)) / n_pat

    treated_full = float(x.groupby("rep")["treat_full"].mean().mean())
    treated_red = float(x.groupby("rep")["treat_red"].mean().mean())

    return {
        "threshold": t,
        "n_patients": n_pat,
        "n_flip_majority": int(len(maj)),
        "pct_flip_majority": round(100.0 * len(maj) / n_pat, 2),
        "newly_recommended": pos_gained + neg_gained,
        "withdrawn": pos_lost + neg_lost,
        "direction_tied": pos_tied + neg_tied,
        "pos_newly_recommended": pos_gained,
        "pos_withdrawn": pos_lost,
        "neg_newly_recommended": neg_gained,
        "neg_withdrawn": neg_lost,
        "pos_withdrawn_meanp": pos_lost_meanp,
        "pos_newly_recommended_meanp": pos_gained_meanp,
        "treated_frac_full": round(treated_full, 4),
        "treated_frac_reduced": round(treated_red, 4),
        "delta_net_benefit": round(d_nb, 5),
        "delta_net_benefit_from_counts": round(d_nb_pred, 5),
    }


def risk_percentiles(d: pd.DataFrame, col: str) -> dict:
    s = d[col]
    return {f"p{int(100 * q)}": round(float(s.quantile(q)), 4) for q in PCTL}


def resolution(d: pd.DataFrame, col: str) -> dict:
    """How many distinct risk values the model can actually emit, per repetition.

    This is the quantity that makes the direction of a decision flip predictable. A model fitted
    on one discrete feature can only place a patient on a handful of points, so a threshold either
    falls between those points -- and every patient on the wrong side stays there -- or lands on
    one of them, and every patient sitting on it has an arbitrary decision. Resolution is not
    recoverable by recalibration: a monotone map of k points is k points.
    """
    per_rep = d.groupby("rep")[col].apply(lambda v: v.round(6).nunique())
    return {"distinct_mean": round(float(per_rep.mean()), 1),
            "distinct_min": int(per_rep.min()),
            "distinct_max": int(per_rep.max())}


def write_table(df: pd.DataFrame, meta: dict) -> None:
    """The mammographic sweep as a bare tabular for the manuscript to \\input."""
    s = df[df.example == "worked_example"].sort_values("threshold")
    out = [r"% auto-generated by experiments/enrichments/compute_flip_decomposition.py",
           r"\begin{tabular}{@{}rrrrrrrr@{}}", r"\toprule",
           r"$t$ & flipped & newly rec. & withdrawn & \multicolumn{2}{c}{of which positive} "
           r"& refer & $\Delta$NB \\",
           r"\cmidrule(lr){5-6}",
           r" &  &  &  & rec. & withdr. & full$\to$red. &  \\", r"\midrule"]
    for _, r in s.iterrows():
        star = r"$^{\dagger}$" if r.preregistered else ""
        out.append(f"{r.threshold:.2f}{star} & {int(r.n_flip_majority)} & "
                   f"{int(r.newly_recommended)} & {int(r.withdrawn)} & "
                   f"{int(r.pos_newly_recommended)} & {int(r.pos_withdrawn)} & "
                   f"{r.treated_frac_full:.2f}$\\to${r.treated_frac_reduced:.2f} & "
                   f"{r.delta_net_benefit:+.4f} \\\\")
    out += [r"\bottomrule", r"\end{tabular}"]
    (ROOT / "paper" / "flip_decomposition_table.tex").write_text(
        "\n".join(out) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((ROOT / "config/analysis.json").read_text(encoding="utf-8"))

    rows, meta = [], {}
    for key in ("worked_example", "secondary_example"):
        c = cfg[key]
        ds, cell = c["dataset"], c["cell"]
        full, red, t0 = c["budget_full"], c["budget_reduced"], float(c["threshold"])
        d = load_poof(ds, cell)

        thresholds = [t0] + [t for t in SWEEP if abs(t - t0) > 1e-9]
        for t in thresholds:
            r = decompose(d, full, red, t)
            r.update(example=key, dataset=ds, preregistered=(abs(t - t0) < 1e-9))
            rows.append(r)

        meta[key] = {
            "dataset": ds, "cell": cell, "threshold_preregistered": t0,
            "prevalence": round(float(d.groupby("patient").y.first().mean()), 4),
            "risk_percentiles_full": risk_percentiles(d, full),
            "risk_percentiles_reduced": risk_percentiles(d, red),
            "resolution_full": resolution(d, full),
            "resolution_reduced": resolution(d, red),
        }
        print(f"{key}: {ds}, prevalence {meta[key]['prevalence']}, "
              f"{len(thresholds)} thresholds; distinct risk values "
              f"{meta[key]['resolution_full']['distinct_mean']:.0f} full -> "
              f"{meta[key]['resolution_reduced']['distinct_mean']:.0f} reduced")

    df = pd.DataFrame(rows)
    cols = ["example", "dataset", "threshold", "preregistered", "n_patients",
            "n_flip_majority", "pct_flip_majority", "newly_recommended", "withdrawn",
            "direction_tied", "pos_newly_recommended", "pos_withdrawn",
            "neg_newly_recommended", "neg_withdrawn", "pos_withdrawn_meanp",
            "pos_newly_recommended_meanp", "treated_frac_full", "treated_frac_reduced",
            "delta_net_benefit", "delta_net_benefit_from_counts"]
    df[cols].to_csv(OUT / "flip_decomposition.csv", index=False, lineterminator="\n")
    (OUT / "flip_decomposition.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8", newline="\n")

    # The two checks worth printing, because they are the claims the paper will make.
    w = df[(df.example == "worked_example") & df.preregistered].iloc[0]
    print(f"\nat the pre-registered t={w.threshold}: {w.n_flip_majority} flips, "
          f"{w.newly_recommended} newly recommended vs {w.withdrawn} withdrawn; "
          f"positives {w.pos_newly_recommended} gained / {w.pos_withdrawn} lost")
    print(f"  dNB measured {w.delta_net_benefit:+.4f} vs "
          f"{w.delta_net_benefit_from_counts:+.4f} predicted from the counts alone")
    worst = df[df.example == "worked_example"].loc[
        df[df.example == "worked_example"].delta_net_benefit.idxmin()]
    print(f"  worst threshold t={worst.threshold}: dNB {worst.delta_net_benefit:+.4f}, "
          f"{worst.pos_withdrawn} positives withdrawn")
    write_table(df, meta)
    print(f"\nwrote {OUT}/flip_decomposition.csv and .json, and paper/flip_decomposition_table.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
