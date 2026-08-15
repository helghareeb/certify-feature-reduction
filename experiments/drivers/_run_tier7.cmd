@echo off
REM Tier 7 n/p disentangle: arrhythmia p=279 fixed, n in {100,150,250}. Resumable (skips existing).
REM Low-priority (launched BelowNormal). n=452 reuses existing summary_arrhythmia.csv.
cd /d C:\research\TASK-014\repo
set PYTHONPATH=src
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set PY=C:\research\_env\nsclin\Scripts\python.exe
if not exist results\tier7 mkdir results\tier7
for %%N in (100 150 250) do (
  if not exist results\tier7\summary_arrhythmia_n%%N.csv (
    echo ----- n=%%N start %DATE% %TIME% ----- >> results\tier7\tier7_driver.log
    %PY% experiments\run_highdim.py --calib config\calibration_tier7_n%%N.json --datasets arrhythmia --calibrations none --out results\tier7\summary_arrhythmia_n%%N.csv --raw results\tier7\raw_arrhythmia_n%%N.csv >> results\tier7\log_n%%N.log 2>&1
    echo TIER7_DONE n=%%N %DATE% %TIME% >> results\tier7\tier7_driver.log
  )
)
echo TIER7_ALL_DONE %DATE% %TIME% >> results\tier7\tier7_driver.log
