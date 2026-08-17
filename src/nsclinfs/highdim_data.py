"""High-dimensional (p >> 44) dataset loaders for the Tier-2 boundary arm (enrichment round).
Same contract as nsclinfs.data loaders: load_*(data_dir) -> (X: DataFrame, y: 0/1 np.ndarray, sensitive: Series).
Raw .mat/.arff files are not redistributed; point NSCLINFS_HIGHDIM_DIR at the directory
holding them, or place them under data/highdim/. Frozen nsclinfs.data is untouched;
register these via nsclinfs.data.LOADERS.update(HIGHDIM_LOADERS) in the high-dim runner only.
Sensitive attribute = constant 'all' (these sets carry no usable subgroup), matching bcw/spectf convention.
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np, pandas as pd

HD = Path(os.environ.get("NSCLINFS_HIGHDIM_DIR", "data/highdim"))

def _mat(fn: str):
    from scipy.io import loadmat
    m = loadmat(str(HD / fn))
    X = np.asarray(m["X"], dtype=float)
    Y = np.asarray(m["Y"]).ravel()
    y = (Y == Y.max()).astype(int)                       # labels coded 1/2 or -1/1 -> 0/1
    Xdf = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    sens = pd.Series(["all"] * len(y), name="none").astype("object")
    return Xdf, y, sens

def load_arcene(data_dir=None):      return _mat("arcene.mat")        # n=200  p=10000
def load_gli85(data_dir=None):       return _mat("GLI-85.mat")        # n=85   p=22283
def load_prostate_ge(data_dir=None): return _mat("Prostate-GE.mat")  # n=102  p=5966
def load_smk_can_187(data_dir=None): return _mat("SMK-CAN-187.mat")  # n=187  p=19993

def load_arrhythmia(data_dir=None, params=None):                      # n=452  p=279 (bridge)
    """Tier-7 note: accepts the SAME subsample convention as load_diabetes130 so n can be
    varied at fixed p=279. params (from config dataset_params.arrhythmia): n_target (or None
    = full 452), subsample_seed, stratify ("outcome" — arrhythmia has no protected subgroup,
    so joint == outcome). Default params=None reproduces the original full-cohort bytes exactly."""
    df = pd.read_csv(HD / "arrhythmia" / "arrhythmia.data", header=None, na_values="?")
    y = (df.iloc[:, -1] != 1).astype(int).to_numpy()                  # class 1 = normal -> 0; 2..16 -> 1
    X = df.iloc[:, :-1].copy()
    X.columns = [f"f{i}" for i in range(X.shape[1])]
    sens = pd.Series(["all"] * len(y), name="none").astype("object")
    p = params or {}
    n_target = p.get("n_target", None)
    # Deterministic stratified subsample, identical idiom to load_diabetes130 (skipped when
    # n_target is None or >= len). Stratify on outcome (no race subgroup here).
    if n_target is not None and len(X) > n_target:
        rng = np.random.RandomState(int(p.get("subsample_seed", 20260626)))
        strata = y  # outcome-only; "outcome_race" collapses to this since race is constant
        idx = (pd.Series(range(len(X))).groupby(strata, group_keys=False)
               .apply(lambda s: s.sample(n=max(1, int(round(len(s) * n_target / len(X)))),
                                          random_state=rng)).to_numpy())
        X, y, sens = X.iloc[idx].reset_index(drop=True), y[idx], sens.iloc[idx].reset_index(drop=True)
    return X, y, sens

HIGHDIM_LOADERS = {
    "arcene": load_arcene, "gli85": load_gli85, "prostate_ge": load_prostate_ge,
    "smk_can_187": load_smk_can_187, "arrhythmia": load_arrhythmia,
}
