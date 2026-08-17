"""The within-unit paired comparison of the Arm B composition ladder.

Exists because the marginal test is the weaker one and fails where this succeeds. Once the
per-cell seed excludes the kept-set size, every rung of the ladder sees the identical
cross-validation splits and the identical base ranking, so the rungs can be differenced
*within* a (ranker, learner, repetition) unit rather than compared by asking whether their
marginal intervals happen to overlap.

That distinction is not cosmetic here. Marginally, the widest two rungs cannot be separated
(their intervals overlap); paired, every adjacent step excludes zero. Reporting the marginal
version would have handed a reviewer a claim they could disprove in a minute while the true,
stronger claim sat unused in the same file.

    python experiments/enrichments/paired_ladder_steps.py
"""
from __future__ import annotations

import math
import os
from collections import defaultdict

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROWS = os.path.join(HERE, "results", "enrichments/12c_kept_set_composition_paired", "p1_arcene_reverse_v4_rows.csv")
OUT = os.path.join(HERE, "results", "derived", "p1_armB_v4_paired_steps.csv")


def main() -> int:
    d = pd.read_csv(ROWS)
    units: dict[tuple, dict[int, float]] = defaultdict(dict)
    for r in d.itertuples():
        units[(r.method, r.classifier, r.rep)][int(r.kept_features)] = float(r.auroc_penalty)

    keeps = sorted({int(k) for k in d.kept_features.unique()})
    complete = [v for v in units.values() if len(v) == len(keeps)]
    print(f"{len(complete)} of {len(units)} units carry all {len(keeps)} rungs")

    steps = list(zip(keeps, keeps[1:])) + [(keeps[0], keeps[-1])]
    rows = []
    for a, b in steps:
        diffs = [v[b] - v[a] for v in complete]
        n = len(diffs)
        m = sum(diffs) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in diffs) / (n - 1))
        se = sd / math.sqrt(n)
        lo, hi = m - 1.96 * se, m + 1.96 * se
        rows.append({"step": f"{a}->{b}", "paired_diff": round(m, 4),
                     "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                     "excludes_zero": bool(lo > 0 or hi < 0), "n_units": n})
        print(f"  {a:>5} -> {b:<6} {m:+.4f}  [{lo:+.4f}, {hi:+.4f}]"
              f"{'  excludes 0' if lo > 0 or hi < 0 else '  spans 0'}  n={n}")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"wrote {os.path.relpath(OUT, HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
