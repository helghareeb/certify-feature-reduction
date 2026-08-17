# Generated figures and table fragments

The manuscript is not distributed in this repository. What is here are the artefacts the
pipeline generates and the manuscript then includes, so that you can rebuild them and compare
against the numbers as they were typeset.

| what | produced by |
|---|---|
| `figures/*.pdf` | `experiments/make_figures.py`, `make_enrichment_figures.py`, `meta_analysis.py`, `worked_example.py`, `ranking_stability.py` |
| `*_table.tex` | the same scripts; each is a bare `tabular` the manuscript `\input{}`s |

Two of the manuscript's figures have no file here because they are drawn in the manuscript
source itself, as TikZ: the protocol architecture and the budget-design schematic. Neither
carries a measured quantity — the second plots $k=\max(1,\operatorname{round}(\mathrm{frac}\cdot p))$
applied to the published feature counts, which you can check against `meta_k_table.tex`.

`silent_cells.tex` is generated but **not** used. It was a table in the first submitted version,
counting the cells where a reliability axis degrades while AUROC does not; a reviewer judged it
redundant against the prose, and the revision states those counts in the text instead. The
generator still writes it, so it is still here, and it should agree with the four counts quoted
in the Results.

To regenerate everything in this directory:

```bash
PYTHONPATH=src python experiments/make_figures.py
PYTHONPATH=src python experiments/make_enrichment_figures.py
PYTHONPATH=src python experiments/meta_analysis.py
PYTHONPATH=src python experiments/meta_analysis_k.py
PYTHONPATH=src python experiments/safe_budget.py
PYTHONPATH=src python experiments/worked_example.py
PYTHONPATH=src python experiments/subsample_agreement.py
PYTHONPATH=src python experiments/ranking_stability.py
```

Re-running writes LF line endings, so a regenerated file can differ from the committed one in
bytes while being identical in every value. See the caveat at the end of
[`../REPRODUCE.md`](../REPRODUCE.md).
