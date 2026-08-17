@echo off
rem Detached v2 burn runner -- executed by Windows Task Scheduler, independent of any
rem interactive session. Fully resumable: launch_grid.py skips every shard whose file
rem already exists with the expected row count, so re-running this script after any
rem interruption continues from the last completed shard. Writes results\BURN_DONE.marker
rem on full success or results\BURN_FAILED.marker on the first failing stage.

cd /d <repo root>
set PYTHONPATH=src
if exist results\BURN_DONE.marker del results\BURN_DONE.marker
if exist results\BURN_FAILED.marker del results\BURN_FAILED.marker
echo === burn (re)start %date% %time% === >> results\burn_detached.log

.venv\Scripts\python.exe experiments\launch_grid.py --calib config/calibration.json --shard-dir results/raw/shards_main --max-workers 6 >> results\burn_detached.log 2>&1
if errorlevel 1 goto :fail
.venv\Scripts\python.exe experiments\merge_shards.py --calib config/calibration.json --shard-dir results/raw/shards_main --raw-out results/raw/audit.csv --out results/summary.csv --nb-out results/cache/nb_curves.parquet >> results\burn_detached.log 2>&1
if errorlevel 1 goto :fail

.venv\Scripts\python.exe experiments\launch_grid.py --calib config/calibration_recal.json --shard-dir results/raw/shards_recal --max-workers 6 >> results\burn_detached.log 2>&1
if errorlevel 1 goto :fail
.venv\Scripts\python.exe experiments\merge_shards.py --calib config/calibration_recal.json --shard-dir results/raw/shards_recal --raw-out results/raw/audit_recal.csv --out results/summary_recalibration.csv --nb-out results/cache/nb_curves_recal.parquet >> results\burn_detached.log 2>&1
if errorlevel 1 goto :fail

.venv\Scripts\python.exe experiments\launch_grid.py --calib config/calibration_subcheck.json --shard-dir results/raw/shards_subcheck --max-workers 6 >> results\burn_detached.log 2>&1
if errorlevel 1 goto :fail
.venv\Scripts\python.exe experiments\merge_shards.py --calib config/calibration_subcheck.json --shard-dir results/raw/shards_subcheck --raw-out results/raw/audit_subcheck.csv --out results/summary_subcheck.csv --nb-out results/cache/nb_curves_subcheck.parquet >> results\burn_detached.log 2>&1
if errorlevel 1 goto :fail

echo === burn COMPLETE %date% %time% === >> results\burn_detached.log
echo done> results\BURN_DONE.marker
exit /b 0

:fail
echo === burn FAILED %date% %time% (see above) === >> results\burn_detached.log
echo failed> results\BURN_FAILED.marker
exit /b 1
