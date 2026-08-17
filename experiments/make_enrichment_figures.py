"""Figures for the second-round controls, from committed results only.

Three findings from this round are more legible as pictures than as sentences, and each
one is the kind a reader checks by eye:

  fig:ladder     recalibration recovers calibration error in proportion to its flexibility
                 and recovers selective reliability at no rung -- a rising curve above a
                 flat line.
  fig:crossaxis  the five reliability axes are not one scale. Ordering-based axes cohere,
                 scale-based axes cohere, and the two blocks are nearly independent. The
                 block structure is visible immediately in a correlation matrix and takes a
                 paragraph to state in prose.
  fig:probedose  injecting pure noise at a fixed budget does not raise the reduction
                 penalty; it lowers it, or reverses its sign. Confidence intervals make the
                 three datasets' different behaviours separable at a glance.

Every input is a committed CSV under results/. No model is fitted here and no number is
computed that is not already in the released artifacts (R1, R2).

    python experiments/make_enrichment_figures.py
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "paper" / "figures"
RES = ROOT / "results"

# One muted palette across all three, so the figures read as a set.
INK = "#1a1a1a"
BLUE = "#2c5f9e"
RED = "#b3402f"
GREY = "#8a8a8a"

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 0.8,
    "figure.dpi": 150,
})


def _finish(fig, path: Path) -> None:
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


# ---------------------------------------------------------------- fig:ladder
def ladder() -> None:
    d = pd.read_csv(RES / "enrichments/11_recalibrator_flexibility_ladder" / "p2_flexibility_ladder.csv")
    d = d.sort_values("flexibility").reset_index(drop=True)
    x = np.arange(len(d))
    labels = [str(c).replace("temperature", "temp.") for c in d["calibrate"]]
    params = ["0", "1", "2", "3", "np"]

    fig, ax = plt.subplots(figsize=(5.0, 3.3))
    ax.axhline(0.0, color=GREY, lw=0.7, ls=":")
    ax.plot(x, d["ece_recovery"], "o-", color=BLUE, lw=1.8, ms=5,
            label="calibration error (ECE)")
    ax.plot(x, d["aurc_recovery"], "s-", color=RED, lw=1.8, ms=5,
            label="selective reliability (AURC)")
    if "net_benefit_recovery" in d:
        ax.plot(x, d["net_benefit_recovery"], "^--", color=GREY, lw=1.2, ms=4,
                label="clinical net benefit")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{a}\n({b})" for a, b in zip(labels, params)])
    ax.set_xlabel("recalibrator, ordered by free parameters")
    ax.set_ylabel("recovery vs uncalibrated\n(positive = improvement)")
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    # the point of the figure, said once on the figure itself
    lo = min(d["aurc_recovery"].min(), 0.0)
    hi = d["ece_recovery"].max()
    pad = 0.28 * (hi - lo)
    ax.set_ylim(lo - pad, hi + pad)
    ax.text(len(x) - 1.05, hi + 0.10 * (hi - lo), "recovery rises with flexibility",
            ha="right", va="bottom", color=BLUE, fontsize=8)
    ax.text(len(x) - 1.05, lo - 0.16 * (hi - lo), "no recovery at any rung",
            ha="right", va="top", color=RED, fontsize=8)
    _finish(fig, FIG / "recalibration_ladder.pdf")


# ------------------------------------------------------------- fig:crossaxis
def crossaxis() -> None:
    d = pd.read_csv(RES / "enrichments/10b_cross_axis_coherence" / "e3_cross_axis_corr.csv", index_col=0)
    pretty = {"ECE": "ECE", "selective_ECE": "selective ECE", "net_benefit": "net benefit",
              "AURC": "AURC", "conformal_setsize": "conformal set size",
              "conformal_eff": "conformal set size"}
    # order so the two blocks are adjacent: scale-defined first, then ordering-defined
    want = ["ECE", "selective_ECE", "net_benefit", "AURC"]
    want += [c for c in d.columns if c.startswith("conformal")]
    want = [c for c in want if c in d.columns]
    m = d.loc[want, want]

    fig, ax = plt.subplots(figsize=(4.4, 3.8))
    im = ax.imshow(m.values, cmap="RdBu_r", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(want)))
    ax.set_yticks(range(len(want)))
    ax.set_xticklabels([pretty.get(c, c) for c in want], rotation=35, ha="right")
    ax.set_yticklabels([pretty.get(c, c) for c in want])
    for i in range(len(want)):
        for j in range(len(want)):
            v = m.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if v > 0.80 else INK)
    # separate the two blocks
    ax.axhline(1.5, color=INK, lw=1.1)
    ax.axvline(1.5, color=INK, lw=1.1)
    cb = fig.colorbar(im, ax=ax, shrink=0.82)
    cb.set_label("Spearman $\\rho$ of the reduction penalty", fontsize=8.5)
    cb.ax.tick_params(labelsize=8)
    _finish(fig, FIG / "cross_axis_matrix.pdf")


# ------------------------------------------------------------- fig:probedose
def probedose() -> None:
    d = pd.read_csv(RES / "enrichments/12_probe_injection_dose_response" / "p1_probe_injection.csv")
    d["dose"] = d["dose"].astype(float)
    fig, ax = plt.subplots(figsize=(5.0, 3.3))
    ax.axhline(0.0, color=GREY, lw=0.8, ls=":")

    styles = {"cleveland": (BLUE, "o-"), "mammographic": (INK, "s-"), "spectf": (RED, "^-")}
    for ds, g in d.groupby("dataset"):
        g = g.sort_values("dose")
        col, mk = styles.get(ds, (GREY, "o-"))
        x = np.arange(len(g))
        ax.plot(x, g["auroc_penalty_mean"], mk, color=col, lw=1.6, ms=5, label=ds)
        ax.fill_between(x, g["ci_lo"], g["ci_hi"], color=col, alpha=0.16, lw=0)

    g0 = d[d.dataset == d.dataset.iloc[0]].sort_values("dose")
    ax.set_xticks(np.arange(len(g0)))
    ax.set_xticklabels([f"{int(v)}$\\times$" for v in g0["dose"]])
    ax.set_xlabel("pure-noise features injected, as a multiple of the original count")
    ax.set_ylabel("AUROC reduction penalty\n(positive = reduction hurts)")
    ax.legend(frameon=False, loc="center left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(-0.058, 0.104)
    ax.text(4.05, 0.034, "harm abolished", ha="right", va="bottom",
            color=BLUE, fontsize=8)
    ax.text(4.05, -0.052, "reduction becomes beneficial", ha="right", va="bottom",
            color=RED, fontsize=8)
    _finish(fig, FIG / "probe_injection_dose.pdf")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="ladder | crossaxis | probedose")
    a = ap.parse_args()
    FIG.mkdir(parents=True, exist_ok=True)
    jobs = {"ladder": ladder, "crossaxis": crossaxis, "probedose": probedose}
    for name, fn in jobs.items():
        if a.only and a.only != name:
            continue
        fn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
