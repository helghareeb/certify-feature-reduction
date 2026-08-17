# Archived v1 results (the Scientific Reports v1.0 submission evidence)

Frozen copies of the aggregate CSVs exactly as submitted on 2026-06-28 (tag
`submitted-2026-06-28`, submission ID <submission reference withheld>).

- `summary.csv` — main grid, calibration hash `1d05f19c68b54cba65d30f45e075ac80298954c3ae03d3a17ac25d6fe18414ec`
- `summary_recalibration.csv` — recalibration control, hash `82fc3197b3b595a1420782ddd9eefbc01b9e279219b75ad42ac3b5a51051d16b`
- v1 configs: `config/submitted-v1/`

The revision (v2) rebuilds the entire grid under a new calibration hash (full Diabetes-130
cohort + exact-k budget arm); these files are the paired reference for the v1-vs-v2 diff in
the response letter and MUST NOT be regenerated or edited. Reproduction status under the
pinned environment (`requirements.lock.txt`): all material verdicts reproduce identically;
logistic-cell means drift <= 5e-5 (LBFGS version sensitivity).
