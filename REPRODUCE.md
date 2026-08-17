# Reproducing this study

Written for three kinds of reader, in increasing order of effort:

| you want to… | go to | time |
|---|---|---|
| **check a number** in the paper without running anything | [§1](#1-check-a-number-without-running-anything) | minutes |
| **re-run one experiment** and get the same answer | [§2](#2-re-run-one-experiment) | minutes to hours |
| **rebuild everything** from raw data | [§3](#3-rebuild-everything) | ~12 hours |

If something here does not work, treat it as a defect in this repository rather than in your setup.

---

## 0. Environment

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.lock.txt      # Windows
# .venv/bin/pip install -r requirements.lock.txt        # Linux / macOS
```

Use `requirements.lock.txt`, not `requirements.txt`. The lock file pins exact versions, and one of
this study's own observations is that logistic-regression estimates move in the fourth decimal across
solver versions — small, documented, and enough to make an unpinned rebuild disagree with the paper in
ways that look like errors and are not.

```bash
export PYTHONPATH="src;experiments"      # Windows: semicolons
# export PYTHONPATH="src:experiments"    # Linux / macOS: colons
```

Confirm the environment before trusting anything it produces:

```bash
python -m pytest tests/ -q               # expect: 21 passed, 6 skipped
```

Six of the 27 need a raw dataset on disk and skip until fetch_data.py has run; after it, all 27 pass. A skip is reported as a skip rather than counted as a pass, so a fresh clone cannot show a hollow green.

The tests are not decoration. They check the budget rule's rounding, that the analysis
**refuses** to combine results carrying different calibration hashes, the closed-form value of each
metric on hand-computed cases, that budgets within a repetition are paired, that equal `k` values are
de-duplicated, and that the leakage firewall holds. If any of them fails, stop.

---

## 1. Check a number without running anything

Every aggregate the paper reports is committed. You do not need to re-run the study to audit it.

**Where the numbers live.** `results/summary.csv` is the canonical aggregate: one row per
(dataset, ranker, learner, budget, outcome), carrying the paired difference against the full-feature
model, its bootstrap interval, the raw and Holm-corrected *p*-values, and the materiality verdict.
The enrichment controls live one folder per experiment under `results/`, each with its own
`MANIFEST.sha256`.

**What each column means.** `PROVENANCE.toml` declares every committed column: either it is cited
in the manuscript, or it is marked out of scope **with a written reason**. There is no third
category. Read that file when a column's meaning is not obvious — including `gini`, whose entry
records that it contradicted an earlier draft and what was done about it.

**Verify integrity first.**

```bash
cd results && sha256sum -c MANIFEST.sha256
```

**Then check the claim.** For example, the paper reports selective reliability materially worse in 94
of 108 cells at the 25 % budget:

```python
import pandas as pd
d = pd.read_csv("results/summary.csv", comment="#")
cells = d[(d.outcome == "aurc") & (d.frac == 0.25) & (d.calibrate == "none")]
print(len(cells), cells.material_worse.sum())        # -> 108 94
```

**Trace any result to its code.**

```bash
python scripts/provenance_map.py            # every result group -> the script that produced it
python scripts/provenance_map.py --check    # non-zero exit if anything is unaccounted for
```

---

## 2. Re-run one experiment

### 2a. An analysis over cached outputs — seconds

Most of the enrichment controls fit no models. They read cached out-of-fold probabilities and
recompute metrics, so they finish immediately:

```bash
python experiments/enrichments/compute_tier8.py        # cross-dataset correlates, partials, LODO
python experiments/enrichments/compute_p2.py           # the recalibrator flexibility ladder
python experiments/enrichments/compute_e3_ASRUN.py     # the cross-axis correlation matrix
python experiments/make_enrichment_figures.py          # the three figures those feed
```

These are the best place to start if you want to disagree with us: change a threshold, add a
recalibrator, re-orient an axis, and see what moves.

### 2b. An experiment that fits models — minutes to hours

Seven scripts fit models. All obey the same firewall as the main grid — imputation, ranking,
standardisation and fitting happen inside the training fold:

```bash
python experiments/enrichments/tier6_distance.py       # distance-to-support confidence
python experiments/enrichments/tier3_run.py --verify   # gates itself, then runs
python experiments/enrichments/tier4_disagreement.py   # ensemble disagreement
```

`tier3_run.py --verify` is worth watching even if you do not need its output. It refuses to produce a
beta-calibration number until it has proved that its own hand-written cross-validation ensemble
reproduces scikit-learn's `CalibratedClassifierCV` to about `1e-9`. That is the shape a new
measurement should have: **validate the instrument against a known one before trusting what it
reads.**

### 2c. The high-dimensional arm

```bash
python experiments/run_highdim.py --calib config/calibration_highdim.json
```

This registers the wide-data loaders and then delegates to the frozen `run_clinical_fs.main()`. It
carries no evaluation logic of its own — deliberately, so that arm cannot drift from the audited
pipeline.

---

## 3. Rebuild everything

```bash
# 1. fetch and hash-verify the raw data (~5 min, network-bound)
python experiments/fetch_data.py
#    every dataset is pinned by URL + SHA-256 in data/<name>/MANIFEST.json, so if a source
#    has changed upstream this fails loudly instead of quietly analysing different bytes.

# 2. the main grid (~5.5 h on 6 workers; resumable, safe to interrupt)
python experiments/launch_grid.py --calib config/calibration.json \
    --shard-dir results/raw/shards_main --max-workers 6
python experiments/merge_shards.py --calib config/calibration.json \
    --shard-dir results/raw/shards_main

# 3. the recalibration control (~3.5 h) and the subsample arm (~1 h)
#    exact invocations and measured runtimes: see the table above

# 4. every figure and table fragment (< 5 min each)
python experiments/make_figures.py
python experiments/make_enrichment_figures.py
python experiments/meta_analysis.py
python experiments/meta_analysis_k.py
python experiments/safe_budget.py
python experiments/worked_example.py
```

On a machine that must run in short bursts, the grid takes repetition chunks and appends:

```bash
python experiments/run_clinical_fs.py --rep-start 0  --rep-end 10
python experiments/run_clinical_fs.py --rep-start 10 --rep-end 20 --append
python experiments/run_clinical_fs.py --rep-start 20 --rep-end 30 --append   # last chunk aggregates
python experiments/run_clinical_fs.py --aggregate-only                       # aggregate without re-running
```

Results stream to disk after each coherent unit and the done-marker is written last, so an
interruption costs the current cell and nothing else; relaunching skips what is already finished.
Raw per-cell rows (`results/raw/`) and raw data (`data/**/raw/`) are deliberately not committed — the
committed summaries are the evidence, and they are small enough to read.

---

## 4. What makes a rebuild match

Four properties do the work. They are worth understanding even if you never re-run anything.

**Seeds exclude the budget.** The per-cell seed derives from (dataset, ranker, learner, repetition)
and *not* from the feature budget. So the full-feature and reduced models in a given repetition see
the identical cross-validation split, and their difference is a paired comparison by construction
rather than by luck. This is the most consequential design decision in the study and it costs
nothing.

**One aggregator.** Every table and figure derives from `results/summary*.csv`. No number is computed
twice by two paths that might disagree.

**The configuration is hashed into the data.** Every results file carries the SHA-256 of the
configuration that produced it, and the analysis **raises** rather than silently merging rows whose
hashes differ. It is enforced by a shared guard and covered by its own test — a test that exists
because that guard spent an earlier version of this study as dead code while the manuscript claimed
it was running.

**Manifests are checked, not assumed.** `sha256sum -c` on a fresh clone is the only integrity claim
worth making.

One caveat when you re-run rather than verify. The committed result files carry the byte content
produced on the machine that ran the grid, and `.gitattributes` marks the results tree `-text`, so a
clone reproduces those bytes exactly whatever your platform. Re-running a script on a different
platform reproduces every *value* identically but may write different line endings, and the file will
then fail `sha256sum -c` while being numerically identical. After a re-run, compare values rather than
bytes. As a worked check: regenerating `results/worked_example.json` from the committed caches on
Linux gives 961 patients, 203 majority flips (21.1 %), 15 of them malignant and 4 moved off biopsy --
the numbers in the manuscript, to the digit.

---

## 5. If you find something wrong

You may. Two claims in this manuscript were withdrawn during a pre-submission audit of the prose
against these files, and a third was corrected — the audit record lists both what changed and
what was deliberately left alone.

If a number here does not match the paper, the most useful report contains: the command you ran, the
value you got, the value you expected, and the output of `python scripts/provenance_map.py`.
