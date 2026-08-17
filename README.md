# certify-feature-reduction

**Research compendium — everything behind the paper, and enough to disagree with it.**

[![verify](https://github.com/helghareeb/certify-feature-reduction/actions/workflows/verify.yml/badge.svg)](https://github.com/helghareeb/certify-feature-reduction/actions/workflows/verify.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21978878.svg)](https://doi.org/10.5281/zenodo.21978878)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](pyproject.toml)
[![Reproducible](https://img.shields.io/badge/numbers-regenerate%20from%20seed-brightgreen.svg)](#reproducibility)
[![Pre-registered](https://img.shields.io/badge/pre--registered-with%20dated%20addendum-blue.svg)](docs/PRE_REGISTRATION.md)
[![Status](https://img.shields.io/badge/status-under%20review-orange.svg)](#the-paper)
[![Datasets](https://img.shields.io/badge/datasets-12%20public%20clinical-lightgrey.svg)](#the-data)

---

## The paper

> **Aggressive feature reduction degrades the selective reliability and clinical net benefit of
> clinical risk models**
> Haitham A. El-Ghareeb · Information Systems Department, Faculty of Computers and Information
> Sciences, Mansoura University, Egypt

**Under review at *Scientific Reports*.**

Archived at Zenodo: [10.5281/zenodo.21978878](https://doi.org/10.5281/zenodo.21978878)
(version-independent; resolves to the current release).

This repository is public at a reviewer's request, so that every number in the manuscript can be
checked against the code and the results that produced it. The manuscript itself is not distributed
here; `paper/` holds only the generated figures and the table fragments it includes, so that a
rebuild can be compared against the numbers as typeset.

## Check something in two minutes

You do not have to run the study to test it. In order of effort:

```bash
git clone https://github.com/helghareeb/certify-feature-reduction && cd certify-feature-reduction

# 1. Do the committed results still hash to what the manifest says? (seconds, no dependencies)
python scripts/make_results_manifest.py --check

# 2. Does every committed result have committed code that produced it? (seconds)
python scripts/provenance_map.py --check

# 3. Read the headline off the canonical aggregate: 108 cells, 94 materially worse on AURC
python -c "import pandas as pd; d=pd.read_csv('results/summary.csv',comment='#'); \
c=d[(d.frac==0.25)&(d.outcome=='aurc')&(d.calibrate=='none')]; \
print(len(c),'cells,',int(c.material_worse.sum()),'materially worse')"

# 4. Regenerate the paper's most quotable number from the committed caches (a minute)
pip install -r requirements.lock.txt
PYTHONPATH=src python experiments/worked_example.py
# -> 961 patients, 203 biopsy decisions moved (21.1 %), 4 malignant cases moved off biopsy
```

Steps 1-3 need no dependencies beyond pandas. Every one of them runs in
[CI](.github/workflows/verify.yml) on each push, so the badge above is a claim about this commit
rather than about the day someone last checked.

If a number here does not match the paper, that is a bug and worth reporting — see
[§5 of REPRODUCE.md](REPRODUCE.md).

## What the study asks

Feature reduction is a near-universal preprocessing step in clinical risk modelling, and it is almost
always certified the same way: show that AUROC barely moves. But discrimination is not what a
deployed risk score is relied upon for. Clinicians act on **calibrated probabilities**; triage
requires a model to **order its own errors**; equitable care requires reliability **across
subgroups**.

So this study asks what the AUROC certificate misses, and answers it as an audit rather than as a
proposal:

| | |
|---|---|
| **Datasets** | 12 public clinical, $n = 155$–$101{,}763$, $p = 3$–$44$ (plus 4 high-dimensional, $p$ up to $22{,}283$, as a separate exploratory arm) |
| **Grid** | 3 feature rankers × 3 learners × 30 paired repetitions × 9 budgets |
| **Budgets** | 100 % → 25 % of features, plus a matched **exact-$k$** arm at $k \in \{1,2,4,8\}$ |
| **Audited axes** | calibration (ECE, Brier) · selective reliability (AURC) · clinical net benefit (decision curves) · conformal set size · subgroup gaps |
| **Statistics** | paired Wilcoxon, Holm-corrected within budget family, **and** a 5000-resample bootstrap CI excluding zero — a result is "material" only if both agree |

## The headline findings

- With a quarter of features retained, degradation is material in most of the 108
  dataset–ranker–learner cells: **selective reliability worse in 94**, net benefit in 80, conformal
  set size in 79, discrimination in 91. Calibration error and subgroup gaps are mixed.
- **The harm tracks the *absolute* retained count, not the fraction.** At a matched $k = 1$, *every*
  dataset is materially harmed — including the wide ones whose fractional budgets never reach that
  regime.
- **It reaches the bedside.** On the mammographic-mass cohort, reduction flips the biopsy decision
  for **one patient in five** at a clinically conventional threshold.
- **No dataset property we measured certifies a budget in advance.** A strict certificate — no
  materially-worse cell on any axis — is attainable for exactly one of twelve datasets. The audit
  itself is the certificate.
- **Recalibration is a partial remedy only.** Across five recalibrators spanning one parameter to
  nonparametric, calibration-error recovery rises strictly with flexibility while selective
  reliability recovers nothing.

### Negative and qualifying results

- **Two-thirds of the measured selective-reliability harm is a property of the probability scale.**
  Under a confidence computed from feature-space distance — which the predicted probability never
  enters — the AURC penalty falls from $+0.0334$ to $+0.0116$. The surviving third holds at
  $p = 7\times10^{-103}$.
- **Noise padding does not increase the harm; it reduces it.** Adding pure-noise features at a fixed
  budget lowered the reduction penalty or reversed its sign, against the pre-registered prediction.
  Reduction defends against noise padding.
- **A scalar signal-concentration index does not order the high-dimensional harm.** It reproduces the
  ordering in 2 of 9 ranker × statistic tests, and 0 of 21 once corrected for width.

## Layout

```
src/nsclinfs/        library — loaders, budget rule, rankers, metrics, fairness, seeds, hashing
experiments/         the canonical pipeline, one script per stage
config/              hashed calibration configs · analysis.json (presentation) · submitted-v1/ (frozen)
results/             committed aggregates, out-of-fold caches, MANIFEST.sha256
  enrichments/       19 controls and extensions — see results/enrichments/README.md
data/<name>/         per-dataset README + MANIFEST.json (URL + SHA-256); raw files fetched, never committed
paper/               main.tex, generated tables, figures, response + cover letters, AUDIT_REPORT.md
docs/                PRE_REGISTRATION.md — frozen, with a dated addendum disclosing every later addition
tests/               27 tests: budget rule, hash refusal, closed-form metrics, pairing, dedupe, leakage firewall
```

## Reproduce

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.lock.txt

PYTHONPATH=src python experiments/fetch_data.py            # fetch + SHA-256-verify all raw data
PYTHONPATH="src;experiments" python -m pytest tests/ -q    # 21 passed, 6 skipped before fetch_data

PYTHONPATH=src python experiments/launch_grid.py  --calib config/calibration.json \
    --shard-dir results/raw/shards_main --max-workers 6    # the grid: hours, resumable
PYTHONPATH=src python experiments/merge_shards.py --calib config/calibration.json \
    --shard-dir results/raw/shards_main                    # verify + aggregate

PYTHONPATH=src python experiments/make_figures.py          # every figure and table fragment
```

Measured runtimes, the recalibration and subsample grids, and chunked runs are in
[`REPRODUCE.md`](REPRODUCE.md).

**To check a number without running anything,** the aggregates in `results/` are committed, and
every column in them is either cited in the manuscript or declared out of scope with a reason in
[`PROVENANCE.toml`](PROVENANCE.toml).

## The data

Twelve public clinical datasets, retrieved June 2026 — ten from the UCI Machine Learning Repository,
plus the Diabetes-130 readmission cohort and the mammographic-mass cohort. **No raw data is
committed.** Each `data/<name>/MANIFEST.json` pins the source URL and a SHA-256, so `fetch_data.py`
either reproduces the exact bytes this study used or fails loudly.

## Reproducibility

Every number regenerates end-to-end from committed code, a committed calibration configuration and a
recorded seed. One canonical aggregator feeds every table and figure. Per-cell seeds exclude the
budget, so full-versus-reduced comparisons are paired by construction.

**Integrity is hash-checked at every stage.** The SHA-256 of the active configuration is stamped into
every results file, and the analysis refuses to combine results carrying different hashes; a
`MANIFEST.sha256` covers the committed results tree and each enrichment folder, so any file can be
verified byte-for-byte from a fresh clone.

The originally submitted grids are frozen under `config/submitted-v1/` and `results/submitted-v1/`,
so the revision can be compared against what the reviewers first saw.

## What is deliberately here, against the usual advice

`results/cache/` is about 95 MB of out-of-fold prediction and net-benefit caches, which a lean
repository would exclude. It is committed because the worked clinical examples are computed from
these caches and from nothing else: without them, the paper's headline finding that reduction flips
roughly one biopsy decision in five could not be regenerated from a clone. That is the check a reader
is most entitled to run, so the caches ship.

The delivery reports under `results/enrichments/` were written as working records on two machines and
have been rewritten for publication. Every finding is preserved, including the results that came out
against the hypothesis that motivated them and the pre-specifications written before the numbers were
computed. No data file was touched: every `.csv` and `.json` under `results/` carries the byte content
and the SHA-256 it was produced under.

## License and citation

MIT — see [`LICENSE`](LICENSE). Cite via [`CITATION.cff`](CITATION.cff); the article reference will be
updated on acceptance.
