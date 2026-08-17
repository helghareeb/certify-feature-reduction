"""Render the graphical-abstract schematic (a conceptual illustration of the finding, not new
data) to paper/figures/graphical_abstract.pdf. Standalone asset for journal submission.

    PYTHONPATH=src python experiments/make_graphical_abstract.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrow, FancyBboxPatch

BLUE, RED, GREY = "#2c6fbb", "#c0392b", "#888888"


def _panel(ax, title):
    ax.set_title(title, fontsize=8.5)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.6)


def main() -> int:
    fig = plt.figure(figsize=(9.2, 3.2))
    fig.suptitle("Aggressive feature reduction (100\\% $\\rightarrow$ 25\\% of features) in clinical "
                 "risk models", fontsize=10, y=0.99)
    gs = fig.add_gridspec(1, 3, left=0.05, right=0.985, top=0.80, bottom=0.20, wspace=0.28)
    x = np.linspace(0, 1, 100)

    # (1) Calibration / reliability diagram
    ax = fig.add_subplot(gs[0]); _panel(ax, "Calibration (reliability)")
    ax.plot([0, 1], [0, 1], ":", color=GREY, lw=1)
    ax.plot(x, x + 0.02 * np.sin(np.pi * x), color=BLUE, lw=1.8, label="full features")
    ax.plot(x, np.clip(x - 0.16 * np.sin(np.pi * x), 0, 1), color=RED, lw=1.8, label="25\\% features")
    ax.set_xlabel("predicted", fontsize=7.5); ax.set_ylabel("observed", fontsize=7.5)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")
    ax.text(0.5, 0.06, "ECE / Brier $\\uparrow$ worse", fontsize=7, color=RED, ha="center")

    # (2) Risk-coverage / selective reliability
    ax = fig.add_subplot(gs[1]); _panel(ax, "Selective reliability (risk--coverage)")
    cov = np.linspace(0.2, 1, 100)
    ax.plot(cov, 0.05 + 0.10 * cov**3, color=BLUE, lw=1.8, label="full features")
    ax.plot(cov, 0.09 + 0.20 * cov**3, color=RED, lw=1.8, label="25\\% features")
    ax.set_xlabel("coverage", fontsize=7.5); ax.set_ylabel("selective risk", fontsize=7.5)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")
    ax.text(0.6, 0.02, "AURC $\\uparrow$ worse\\n(survives recalibration)", fontsize=7, color=RED, ha="center")

    # (3) Subgroup gap + AUROC-flat
    ax = fig.add_subplot(gs[2]); _panel(ax, "Subgroup gap \\& discrimination")
    ax.bar([0.25, 0.75], [0.78, 0.80], width=0.18, color=BLUE, label="full")
    ax.bar([0.45, 0.95], [0.66, 0.79], width=0.18, color=RED, label="25\\%")
    ax.annotate("", xy=(0.95, 0.79), xytext=(0.45, 0.66),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8))
    ax.text(0.7, 0.5, "gap widens\\n(equity)", fontsize=7, ha="center", color=RED)
    ax.text(0.6, 0.92, "AUROC barely moves", fontsize=7, ha="center", color=BLUE)
    ax.set_ylim(0, 1); ax.set_ylabel("metric by subgroup", fontsize=7.5)

    fig.text(0.5, 0.045,
             "Discrimination looks fine, yet calibration, selective reliability, and equity silently "
             "degrade --- and recalibration repairs the calibration dial, not the risk--coverage curve.",
             ha="center", fontsize=8.2, style="italic")

    out = Path("paper/figures/graphical_abstract.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"[graphical abstract] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
