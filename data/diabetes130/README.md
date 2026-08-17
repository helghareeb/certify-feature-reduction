# Diabetes 130-US hospitals (1999-2008)

Source: UCI ML Repository dataset 296 (Strack et al. 2014). Retrieved 2026-06-27:
https://archive.ics.uci.edu/ml/machine-learning-databases/00296/dataset_diabetes.zip
Target: early readmission (<30 days). Protected: race. Raw gitignored.

Cohort: 101,766 encounters; 101,763 after dropping gender = "Unknown/Invalid".
v1 (submitted 2026-06-28) used a deterministic outcome-stratified subsample of 6,000
(seed 20260626) — an earlier note here said "~12k", which was wrong; the code always said 6,000.
v2 (revision) analyzes the FULL cohort; the subsample survives only as a robustness arm,
now jointly stratified by (outcome, race). All of this is config-driven
(`dataset_params.diabetes130` in `config/calibration.json`) and covered by the calibration hash.
