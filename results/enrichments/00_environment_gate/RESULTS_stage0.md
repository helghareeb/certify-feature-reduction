# RESULTS — Stage 0 (the gate) — PASS

**Run:** second compute node · **2026-08-13 ~03:1x AST**
**Code:** commit `e073ad5` (branch revision-sr-r1), sha256 of archive verified `1b9890b4…`.

## The four gate checks
1. **Environment** — `pip install -r requirements.lock.txt` into a dedicated venv (Python 3.13.13).
   All 27 pinned versions match (numpy 2.5.1, scipy 1.18.0, scikit-learn 1.9.0, pandas 3.0.3, joblib 1.5.3, …). Freeze in `env_freeze.txt`.
2. **Data** — `fetch_data.py`: **12/12 datasets fetched, 12/12 sha256-verified against MANIFEST.json, 0 failures.**
3. **Tests** — `pytest -q`: **27 passed** (leakage firewall = label-permutation collapses AUROC to chance; seed determinism; metric bounds). 1 harmless SyntaxWarning in make_figures.py (not a test).
4. 🎯 **Reproduction gate — BYTE-IDENTICAL.** Re-ran the cleveland spotcheck with the committed
   v2 config (`results/spotcheck_v2/calib_cleveland_v2code.json`), REPS=30, aggregated, and diffed
   the frac-arm cells against committed `results/summary.csv`:
   - **540 cleveland frac-arm cells matched; 5,292 value comparisons; all 5,292 byte-identical; max |diff| = 0.000e+00** across mean/ci/delta/cohens_d/diff_ci/p_raw/p_holm/k/n.
   - (config hashes differ by design — the spotcheck config sets `budgets.ks=[]`, dropping the exact-k arm; comparison is on the frac arm, which is the intended reference. Numbers are exact.)

**Verdict: environment is byte-identical to the committed reference → results here are mergeable → cleared for Tier 1.**

## Notes
- Datasets live under `<repo root>\data\` (local `C:`, not synced) per the data-placement rule.
- GPU untouched (pure CPU scikit-learn). Machine: i7-12700F 20 threads, ~15.8 GB RAM — workers will be sized against free RAM for Tier 1.
- gate_diff.txt included (full per-column diff table).
