# Reproduce

```bash
# 1. environment
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 2. data (gitignored; see data/cleveland/README.md for source + license)
mkdir -p data/cleveland/raw
curl -sSL https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data \
  -o data/cleveland/raw/processed.cleveland.data

# 3. tests (leakage firewall, seed determinism, metric bounds)
PYTHONPATH=src pytest -q

# 4. run the audit -> results/summary.csv (canonical, R2) + results/summary.headline.json
PYTHONPATH=src python experiments/run_clinical_fs.py
```

The run is deterministic (per-cell seeds from `config/calibration.json:RANDOM_SEED`, R5) and its config
content-hash is embedded in every results CSV (R6). On a busy/slow machine the grid can be run in reps
chunks under any per-command time limit, e.g.:

```bash
PYTHONPATH=src python experiments/run_clinical_fs.py --rep-start 0  --rep-end 10
PYTHONPATH=src python experiments/run_clinical_fs.py --rep-start 10 --rep-end 20 --append
PYTHONPATH=src python experiments/run_clinical_fs.py --rep-start 20 --rep-end 30 --append   # last chunk aggregates
# or aggregate an existing raw without re-running:
PYTHONPATH=src python experiments/run_clinical_fs.py --aggregate-only
```

Raw per-cell rows (`results/raw/`) and raw data (`data/**/raw/`) are gitignored; the committed
`results/summary.csv` is the single source for every reported number (R1/R2). `STATUS: validated` requires
REPS >= 30 (R4/N14).
