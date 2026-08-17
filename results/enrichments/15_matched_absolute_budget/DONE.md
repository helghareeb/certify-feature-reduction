# DONE — P5, matched absolute budget (two deliveries, both kept)

At a **fixed** retained count, reduction harm still rises with the candidate-set size $p$. That
separates "few candidate features" from "few retained features", which the fractional budget rule
links mechanically.

This folder holds two deliveries. The second supersedes the first for what the manuscript reports,
and the first is kept because it is the record the conclusion was first drawn from.

| delivery | files | what it measured |
|---|---|---|
| first | `RESULTS_p5.md`, `p5_harm_at_absolute_k8.csv`, `p5_summary.json` | $\rho(p,\text{harm})$ at $k{=}8$ only |
| second (**cited**) | `RESULTS_p5_across_budgets.md`, `p5_width_across_budgets.csv`, `p5_width_across_budgets.json`, `p5_width_rows.csv`, `compute_p5_across_budgets.py` | the same association at every matched budget $k\in\{1,2,4,8\}$ |

## Which number is which

Two different quantities both round to $+0.60$, so they are worth stating apart.

| value | budget | dataset set | file | in the manuscript? |
|---|---|---|---|---|
| $\rho=+0.598$, $p=0.031$ | $k{=}8$ | 13, clinical **pooled with the high-dimensional arm** | `p5_summary.json` (`..._k8_all`) | **no** — declared out of scope; the two panels are never pooled |
| $\rho=+0.765$, $p=0.016$ | $k{=}8$ | 9 clinical (only those with $p>8$) | both deliveries | yes |
| $\rho=+0.600$, $p=0.039$ | $k{=}2$ | **all 12** clinical | `p5_width_across_budgets.csv` | **yes** — this is the $+0.60$ the paper quotes |
| $\rho=+0.323$, $p=0.306$ | $k{=}1$ | all 12 clinical | `p5_width_across_budgets.csv` | yes, as the non-significant case |

The manuscript's $+0.60$ is therefore the twelve-dataset value at $k{=}2$, not the pooled value at
$k{=}8$. The second delivery is what removed the earlier nine-of-twelve restriction: at $k{=}2$ the
association is material on the whole panel, including the three narrowest datasets that a $k{=}8$
budget has to drop.

At $k{=}1$ the association is not significant, and that is coherent rather than a failure: reducing
every dataset to one feature harms all of them regardless of width, so width has nothing left to
order.

Both deliveries are cache-only re-analyses of `results/summary.csv`. No model was fitted.
