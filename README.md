# certify-feature-reduction

**Research compendium — everything behind the paper, and enough to disagree with it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-27%20passing-brightgreen.svg)](tests/)
[![Reproducible](https://img.shields.io/badge/numbers-regenerate%20from%20seed-brightgreen.svg)](#reproducibility-rules-enforced-not-aspirational)
[![Pre-registered](https://img.shields.io/badge/pre--registered-with%20dated%20addendum-blue.svg)](docs/PRE_REGISTRATION.md)
[![Status](https://img.shields.io/badge/status-under%20review-orange.svg)](#the-paper)
[![Datasets](https://img.shields.io/badge/datasets-12%20public%20clinical-lightgrey.svg)](#the-data)

---

## The paper

> **Aggressive feature reduction degrades the selective reliability and clinical net benefit of
> clinical risk models**
> Haitham A. El-Ghareeb · Information Systems Department, Faculty of Computers and Information
> Sciences, Mansoura University, Egypt

**Submitted to *Scientific Reports*. Under review — revised manuscript.**
Reference `2650209c-ff1e-4df4-aeb0-75ef3b35e564`.

This repository is public **at the reviewers' request**, so that every claim can be checked against
the code that produced it rather than taken on the manuscript's word.

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

### Findings that went against us, kept in

A compendium that contains only supporting evidence is not evidence. These are in the paper at full
prominence:

- **Two-thirds of the measured selective-reliability harm is a property of the probability scale.**
  Recomputed under a confidence taken from feature-space distance — which the model's predicted
  probability never enters — the AURC penalty falls from $+0.0334$ to $+0.0116$. The surviving third
  holds at $p = 7\times10^{-103}$.
- **A pre-registered causal prediction failed.** Padding a dataset with pure-noise features was
  predicted to increase the harm. It *decreased* it, or reversed its sign. Reduction defends against
  noise padding, and the registered prediction is reported as refuted.
- **A proposed explanation was withdrawn before submission.** A scalar signal-concentration index was
  claimed to order the high-dimensional harm; it reproduces the ordering in 2 of 9 tests, and **0 of
  21** once corrected for the width incomparability that caused the failure.

## Layout

```
src/nsclinfs/        library — loaders, budget rule, rankers, metrics, fairness, seeds, hashing
experiments/         the canonical pipeline, one script per stage
config/              hashed calibration configs · analysis.json (presentation) · submitted-v1/ (frozen)
results/             committed aggregates + caches + MANIFEST.sha256
  enrichments/       13 controls and extensions — see results/enrichments/README.md
data/<name>/         per-dataset README + MANIFEST.json (URL + SHA-256); raw files fetched, never committed
paper/               main.tex, generated tables, figures, response + cover letters, AUDIT_REPORT.md
docs/                PRE_REGISTRATION.md — frozen, with a dated addendum disclosing every later addition
tests/               27 tests: budget rule, hash refusal, closed-form metrics, pairing, dedupe, leakage firewall
```

## Reproduce

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.lock.txt

PYTHONPATH=src python experiments/fetch_data.py            # fetch + SHA-256-verify all raw data
PYTHONPATH="src;experiments" python -m pytest tests/ -q    # 27 tests

PYTHONPATH=src python experiments/launch_grid.py  --calib config/calibration.json \
    --shard-dir results/raw/shards_main --max-workers 6    # the grid: hours, resumable
PYTHONPATH=src python experiments/merge_shards.py --calib config/calibration.json \
    --shard-dir results/raw/shards_main                    # verify + aggregate

PYTHONPATH=src python experiments/make_figures.py          # every figure and table fragment
```

Measured runtimes, the recalibration and subsample grids, and chunked runs are in
[`REPRODUCE.md`](REPRODUCE.md) and `paper/LOCAL_EXECUTION_PLAYBOOK.md`.

**To check a number without running anything,** the aggregates in `results/` are committed. Every
column in every committed results file is either cited in the manuscript or declared out of scope
**with a written reason** in `paper/MANIFEST.toml` — including one column that contradicted an
earlier draft and caused a claim to be withdrawn.

## The data

Twelve public clinical datasets, retrieved June 2026 — ten from the UCI Machine Learning Repository,
plus the Diabetes-130 readmission cohort and the mammographic-mass cohort. **No raw data is
committed.** Each `data/<name>/MANIFEST.json` pins the source URL and a SHA-256, so `fetch_data.py`
either reproduces the exact bytes this study used or fails loudly.

## Reproducibility rules (enforced, not aspirational)

| | |
|---|---|
| **R1** | A number is reported only when it regenerates end-to-end from committed code, the calibration config, and a recorded seed. |
| **R2** | One canonical aggregator — every table and figure derives from the committed summaries. |
| **R5** | Deterministic per-cell seeds; **the seed excludes the budget**, so every comparison is paired by construction rather than by luck. |
| **R6** | The SHA-256 of the active config is stamped into every results file, and the analysis **refuses to combine results carrying different hashes** — enforced by a shared guard at every path that reads a summary for a manuscript number, and covered by a dedicated test. |

The originally submitted grids are frozen under `config/submitted-v1/` and `results/submitted-v1/`
and are never regenerated, so the revision can be compared against what the reviewers first saw.

## Audit

`paper/AUDIT_REPORT.md` records a pre-resubmission audit of the manuscript **against this repository**
— not against itself. It lists every change by issue type with before → after and, more importantly,
everything deliberately **not** changed and why. It found, among other things, a results column that
refuted a claim in the paper, a Discussion sentence recommending a criterion the same paper retracts
two sections earlier, and a stale claim in the cover letter. All three are fixed, and all three are
disclosed in the response to reviewers.

## Compute

Part of the enrichment grid in `results/enrichments/` was executed on a **second machine**, under
configurations, pre-registrations and scripts fixed in advance and committed here. This is a hardware
arrangement and nothing more: no one other than the author contributed to the design, analysis or
interpretation of this study.

Every result returned from that machine was re-verified by SHA-256 manifest on the author's box and
independently recomputed from its raw per-unit outputs before any number entered the manuscript. The
scripts that produced them are in `experiments/enrichments/`, so the method can be read and not only
the numbers checked.

## License and citation

MIT — see [`LICENSE`](LICENSE). Cite via [`CITATION.cff`](CITATION.cff); the article reference will be
updated on acceptance.
