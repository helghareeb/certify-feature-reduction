@echo off
rem Detached recalibration-control burn, ALL THREE RANKERS -- executed by Windows Task
rem Scheduler, independent of any interactive session. Removes the single-ranker
rem restriction that Section 4.8 currently states as a limitation.
rem
rem Fully resumable, exactly like run_burn.cmd: launch_grid.py skips every shard whose
rem file already exists with the expected row count, so re-running this after any
rem interruption (or a reboot) continues from the last completed shard.
rem
rem max-workers is 4, not the burn's 6. HISTORY, because the number has moved twice and
rem the reason matters more than the value: launched at 4; throttled to 2 in 3f08b61 when
rem free physical memory fell to 0.49 GB with the diabetes130 random-forest shards -- the
rem memory-heavy ones -- still ahead; raised back to 4 in d7af698. (That commit left this
rem comment saying 2; corrected here 2026-08-12.)
rem
rem THE RULE, not the number: a swapping worker is slower than no worker, so the width
rem must be set against FREE RAM AT THE TIME, not against core count. Measured on this
rem box: the diabetes130 rf shards are the memory-heavy ones and 4 workers need roughly
rem 6-7 GB free to clear them without swapping. Check before raising:
rem   powershell "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"
rem Raise to 6 only with ~10 GB free. The run is resumable and skips completed shards, so
rem stopping and restarting at a different width costs nothing but the shards in flight --
rem which for an rf shard is up to ~77 min, so prefer to change width between shards.
rem
rem Writes results\RECAL_ALLRANKERS_DONE.marker on success,
rem results\RECAL_ALLRANKERS_FAILED.marker on the first failing stage.

cd /d <repo root>
set PYTHONPATH=src
if exist results\RECAL_ALLRANKERS_DONE.marker del results\RECAL_ALLRANKERS_DONE.marker
if exist results\RECAL_ALLRANKERS_FAILED.marker del results\RECAL_ALLRANKERS_FAILED.marker
echo === recal-allrankers (re)start %date% %time% === >> results\recal_allrankers.log

.venv\Scripts\python.exe experiments\launch_grid.py --calib config/calibration_recal_allrankers.json --shard-dir results/raw/shards_recal_all --max-workers 4 >> results\recal_allrankers.log 2>&1
if errorlevel 1 goto :fail
.venv\Scripts\python.exe experiments\merge_shards.py --calib config/calibration_recal_allrankers.json --shard-dir results/raw/shards_recal_all --raw-out results/raw/audit_recal_all.csv --out results/summary_recalibration_allrankers.csv --nb-out results/cache/nb_curves_recal_all.parquet >> results\recal_allrankers.log 2>&1
if errorlevel 1 goto :fail

echo === recal-allrankers COMPLETE %date% %time% === >> results\recal_allrankers.log
echo done> results\RECAL_ALLRANKERS_DONE.marker
exit /b 0

:fail
echo === recal-allrankers FAILED %date% %time% (see above) === >> results\recal_allrankers.log
echo failed> results\RECAL_ALLRANKERS_FAILED.marker
exit /b 1
