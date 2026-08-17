# LOCAL_EXECUTION_PLAYBOOK — validated commands + measured runtimes (N10)

Every command below was executed for the v2 revision (2026-08-11) on the reference machine
(8 logical cores, 16 GB RAM, Windows 11; Python 3.12.6, packages per `requirements.lock.txt`).
Runtimes are measured, not estimated. Prefix all commands with `PYTHONPATH=src` (Git Bash) or
`set PYTHONPATH=src` (cmd), from the repository root, inside the pinned venv.

## 0. Data + tests (one-time, ~10 min)

| step | command | measured |
|---|---|---|
| fetch + pin all raw datasets | `python experiments/fetch_data.py` (`--verify-only` thereafter) | ~5 min (network-bound) |
| test suite | `PYTHONPATH="src;experiments" python -m pytest tests/ -q` | 27 passed, ~45 s |
| timing probe (optional, diagnostic) | `python experiments/probe_timing.py` | ~4 min |

## 1. The grids (the burn) — resumable, session-independent

One command runs all three grids end to end via the Windows Task Scheduler wrapper
(`experiments\run_burn.cmd`; writes `results/BURN_DONE.marker` on success), or run the stages
manually:

| grid | launch | merge+aggregate | measured wall-clock (6 workers) |
|---|---|---|---|
| main (12 datasets × 3×3 × 30 reps × 9 budgets) | `python experiments/launch_grid.py --calib config/calibration.json --shard-dir results/raw/shards_main --max-workers 6` | `python experiments/merge_shards.py --calib config/calibration.json --shard-dir results/raw/shards_main --raw-out results/raw/audit.csv --out results/summary.csv --nb-out results/cache/nb_curves.parquet` | ~5.5 h (diabetes130 RF shards ~76 min each) |
| recalibration control | same, `--calib config/calibration_recal.json --shard-dir results/raw/shards_recal` | `--raw-out results/raw/audit_recal.csv --out results/summary_recalibration.csv --nb-out results/cache/nb_curves_recal.parquet` | ~3.5 h (full-cohort rf×isotonic shards ~109 min) |
| subsample robustness arm | same, `--calib config/calibration_subcheck.json --shard-dir results/raw/shards_subcheck` | `--raw-out results/raw/audit_subcheck.csv --out results/summary_subcheck.csv --nb-out results/cache/nb_curves_subcheck.parquet` | ~1 h |

Each shard is one invocation of `experiments/run_clinical_fs.py` (the canonical runner and
aggregator) with `--datasets/--methods/--classifiers` filters; the merge step finishes by calling
`python experiments/run_clinical_fs.py --aggregate-only --calib <config> --raw <audit.csv> --out
<summary.csv>` (re-run 2026-08-11 for all three grids to stamp the canonical R6 header; aggregate
values unchanged). Re-running a launcher after any interruption resumes: completed shards are
skipped by expected row count; shard writes are atomic. Full-burn totals: 87 + 29 + 54 shards,
0 failures, ~10 h wall-clock end to end.

## 2. Analyses and every manuscript artifact (all < 5 min each)

| artifact | command |
|---|---|
| Fig 2 + headline/datasets/per-dataset/new-axes/recal tables | `python experiments/make_figures.py` |
| meta table + two-panel Fig (meta_harm.pdf) | `python experiments/meta_analysis.py` |
| retained-k reanalysis + robustness (meta_k.json, meta_k_table) | `python experiments/meta_analysis_k.py` |
| strict-certificate table (safe_budget_table) | `python experiments/safe_budget.py` |
| worked example: tables + decision-curve/flip-CDF/reliability figures | `python experiments/worked_example.py` |
| subsample-agreement table | `python experiments/subsample_agreement.py` |
| selection-stability figure (stability_harm.pdf) | `python experiments/ranking_stability.py --workers 6` (~40 min first run; cached parquet thereafter) |
| the three enrichment figures (recalibration ladder, cross-axis matrix, probe-injection dose-response) | `python experiments/make_enrichment_figures.py` (~5 s; committed CSVs only, fits nothing) |
| cover letter plain-text version, generated from the .tex so the two cannot drift | `python experiments/mk_cover_txt.py` (run 2026-08-15; writes `paper/cover_letter.txt`, no manuscript number) |
| public-compendium sync check (no manuscript number; `--check` exits non-zero if normalisation is due) | `python scripts/sync_public.py --check` (run 2026-08-16) |
| results manifest (write / verify) | `python scripts/make_results_manifest.py [--check]` (run 2026-08-16) |
| external archive: mirror both repos + intermediates + the delivery channel, then re-hash **by reading back from the destination** | `python scripts/sync_archive.py [--verify]` (run 2026-08-16; incremental, so an update after a small change takes seconds) |
| provenance map: every result -> its producing script | `python scripts/provenance_map.py --check` (run 2026-08-16) |
| v1-vs-v2 invariance report | `python experiments/v1_v2_diff.py` |


## 2b. Enrichment controls (`experiments/enrichments/`)

All ran on a second machine 2026-08-13..16 under the pinned environment, against the configurations
in `config/` whose `calibration_sha256` is stamped into each output. Each result folder under
`results/enrichments/` carries the as-run copy of its script plus a `MANIFEST.sha256`; the copies
here resolve the repository root from `__file__` so they run from a clone (`NSCLINFS_REPO` overrides).

| script | produces | note |
|---|---|---|
| `compute_tier1.py`, `compute_tier1_materiality.py` | ECE bin sweep, logistic + random forest | cache-only |
| `compute_tier5.py`, `compute_tier5_materiality.py` | the same sweep for gradient boosting | cache-only |
| `tier3_run.py` | beta + temperature recalibration | fits models; gates its own machinery against `CalibratedClassifierCV` before trusting it |
| `tier4_disagreement.py` | ensemble-disagreement confidence | fits models, in-fold |
| `tier6_distance.py` | distance-to-training-support confidence | fits models; neighbours drawn from the training fold only |
| `compute_tier7.py` | penalty versus $n$ at fixed $p$ | aggregation only |
| `run_highdim.py` + `src/nsclinfs/highdim_data.py` | the high-dimensional grid (arcene, gli85, prostate_ge, arrhythmia) | registers the loaders and then **delegates to the frozen `run_clinical_fs.main()`** — it carries no evaluation logic of its own, so this arm inherits the audited pipeline verbatim |
| `experiments/drivers/*.sh`, `_run_tier7.cmd` | the shell drivers that launched the high-dimensional and arrhythmia-subsampling runs | recorded as run |
| `compute_tier8.py` | cross-dataset correlates, partials, LODO, bootstrap | analysis only |
| `compute_tier9.py` | concentration index | scores recomputed per training fold |
| `compute_e2.py` | independence versus cohort size | cache-only |
| `compute_e3_ASRUN.py` | cross-axis correlation matrix | cache-only |
| `compute_p2.py`, `_verify_p2.py` | recalibrator flexibility ladder + its cross-check | cache-only |
| `compute_p3_ASRUN.py` | pre-registered safe-budget diagnostic | cache-only |
| `compute_p4_ASRUN.py` | localisation of the surviving penalty | cache-only |
| `compute_p5_ASRUN.py` | matched absolute budget | cache-only |
| `compute_p6.py` | combined-confidence arm | not yet in the manuscript |
| `paired_ladder_steps.py` | the within-unit paired comparison of the Arm B ladder | analysis only; possible only because the v4 seed excludes the kept-set size |
| `compute_p1.py`, `compute_p1_v2.py` | probe-injection dose-response (Arm A) and the superseded Arm B | Arm A is in the manuscript; **Arm B is not** — its kept set was selected outside the cross-validation |
| `compute_p1b_v3.py` | Arm B re-run with in-fold kept-set selection | running |
## 3. Manuscript + response letter

```
cd paper && pdflatex -interaction=nonstopmode main.tex   (x3; 19 pp, 0 errors, 0 undefined)
             pdflatex -interaction=nonstopmode response_to_reviewers.tex
```

## Provenance

- Config hashes (embedded in every results CSV header + `calib_sha256` column): main
  `c7ed5da5…`, recal `2c53ce97…`, subcheck `816d180e…`. The originally submitted (v1) configs
  and aggregates are frozen under `config/submitted-v1/` + `results/submitted-v1/` (hashes
  `1d05f19c…`, `82fc3197…`) and are never regenerated.
- Raw per-cell CSVs are gitignored by design; the committed evidence set is the three summary
  CSVs, `results/cache/nb_curves.parquet`, `results/cache/poof/` (per-patient probabilities for
  the two configured worked-example cells), `results/cache/rankings/`, and the JSON reports
  under `results/`.
