"""Tier-2 high-dim runner: registers the high-dim loaders onto nsclinfs.data.LOADERS
(frozen data.py untouched), then delegates to the frozen run_clinical_fs.main()."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nsclinfs import data, highdim_data
data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)
import importlib.util
spec = importlib.util.spec_from_file_location("rcfs", Path(__file__).resolve().parent / "run_clinical_fs.py")
rcfs = importlib.util.module_from_spec(spec); spec.loader.exec_module(rcfs)
raise SystemExit(rcfs.main())
