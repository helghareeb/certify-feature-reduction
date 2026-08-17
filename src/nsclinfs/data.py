"""Public clinical tabular datasets, with a protected attribute where available.

Each loader returns (X, y, sensitive): X a numeric feature frame, y a 0/1 target, and
`sensitive` a categorical Series naming each row's subgroup (a single constant group when
the dataset carries no protected attribute, so fairness gaps are simply undefined there).
The protected attribute is never used as a model feature. Raw files live under
data/<name>/raw/ and are gitignored; see each data/<name>/README.md.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

_CLEVELAND_COLS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]


def load_cleveland(data_dir: str | Path = "data/cleveland") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """UCI Cleveland heart disease. Target: any-disease (num>0). Protected: sex."""
    raw = Path(data_dir) / "raw" / "processed.cleveland.data"
    df = pd.read_csv(raw, header=None, names=_CLEVELAND_COLS, na_values="?").apply(pd.to_numeric, errors="coerce")
    df = df[df["num"].notna()].reset_index(drop=True)
    y = (df["num"].to_numpy() > 0).astype(int)
    sex = df["sex"].map({1.0: "male", 0.0: "female"}).astype("object")
    return df.drop(columns=["num", "sex"]), y, pd.Series(sex, name="sex")


_PIMA_COLS = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age", "outcome"]


def load_pima(data_dir: str | Path = "data/pima") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Pima Indians diabetes (all female). Target: Outcome. Protected: age group (<40 / >=40)."""
    df = pd.read_csv(Path(data_dir) / "raw" / "pima.csv", header=None, names=_PIMA_COLS)
    for c in ["glucose", "bp", "skin", "insulin", "bmi"]:           # physiologically-impossible 0 -> missing
        df[c] = df[c].replace(0, np.nan)
    y = df["outcome"].astype(int).to_numpy()
    sens = pd.Series(np.where(df["age"] >= 40, "age>=40", "age<40"), name="age_group").astype("object")
    return df.drop(columns=["outcome"]), y, sens


_ILPD_COLS = ["age", "gender", "tb", "db", "alkphos", "sgpt", "sgot", "tp", "alb", "ag_ratio", "selector"]


def load_ilpd(data_dir: str | Path = "data/ilpd") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """UCI Indian Liver Patient. Target: liver patient (selector==1). Protected: gender."""
    df = pd.read_csv(Path(data_dir) / "raw" / "ilpd.csv", header=None, names=_ILPD_COLS)
    gender = df["gender"].astype(str).str.strip().str.lower()
    y = (pd.to_numeric(df["selector"], errors="coerce") == 1).astype(int).to_numpy()
    X = df.drop(columns=["gender", "selector"]).apply(pd.to_numeric, errors="coerce")
    return X, y, pd.Series(gender.values, name="gender").astype("object")


def load_heartfailure(data_dir: str | Path = "data/heartfailure") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """UCI Heart-Failure clinical records. Target: DEATH_EVENT. Protected: sex."""
    df = pd.read_csv(Path(data_dir) / "raw" / "heartfailure.csv")
    y = df["DEATH_EVENT"].astype(int).to_numpy()
    sens = df["sex"].map({1: "male", 0: "female"}).astype("object")
    return df.drop(columns=["DEATH_EVENT", "sex"]), y, pd.Series(sens, name="sex")


def load_wdbc(data_dir: str | Path = "data/wdbc") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Wisconsin Diagnostic Breast Cancer (sklearn-bundled). Target: malignant. No protected attribute."""
    from sklearn.datasets import load_breast_cancer
    d = load_breast_cancer(as_frame=True)
    y = (d.target == 0).astype(int).to_numpy()                       # sklearn target: 0=malignant -> y=1 malignant
    sens = pd.Series(["all"] * len(y), name="none").astype("object")  # no subgroup -> fairness gaps undefined
    return d.data.copy(), y, sens


_STATLOG_COLS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
                 "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]


def load_statlogheart(data_dir: str | Path = "data/statlogheart") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Statlog (Heart) disease. Target: presence (num==2). Protected: sex."""
    df = pd.read_csv(Path(data_dir) / "raw" / "heart.dat", sep=r"\s+", header=None, names=_STATLOG_COLS)
    y = (df["num"] == 2).astype(int).to_numpy()
    sex = df["sex"].map({1.0: "male", 0.0: "female"}).astype("object")
    return df.drop(columns=["num", "sex"]), y, pd.Series(sex, name="sex")


def load_haberman(data_dir: str | Path = "data/haberman") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Haberman breast-cancer survival. Target: died within 5y (status==2). Protected: age group."""
    df = pd.read_csv(Path(data_dir) / "raw" / "haberman.data", header=None,
                     names=["age", "op_year", "nodes", "status"])
    y = (df["status"] == 2).astype(int).to_numpy()
    sens = pd.Series(np.where(df["age"] >= 60, "age>=60", "age<60"), name="age_group").astype("object")
    return df.drop(columns=["status"]), y, sens


_HEPATITIS_COLS = ["target", "age", "sex", "steroid", "antivirals", "fatigue", "malaise",
                   "anorexia", "liver_big", "liver_firm", "spleen", "spiders", "ascites",
                   "varices", "bilirubin", "alk_phosphate", "sgot", "albumin", "protime", "histology"]


def load_hepatitis(data_dir: str | Path = "data/hepatitis") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """UCI Hepatitis. Target: death (target==1). Protected: sex."""
    df = pd.read_csv(Path(data_dir) / "raw" / "hepatitis.data", header=None, names=_HEPATITIS_COLS,
                     na_values="?")
    y = (df["target"] == 1).astype(int).to_numpy()
    sex = df["sex"].map({1: "male", 2: "female"}).astype("object")
    X = df.drop(columns=["target", "sex"]).apply(pd.to_numeric, errors="coerce")
    return X, y, pd.Series(sex.values, name="sex")


_MAMMO_COLS = ["birads", "age", "shape", "margin", "density", "severity"]


def load_mammographic(data_dir: str | Path = "data/mammographic") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Mammographic Mass. Target: malignant (severity==1). Protected: age group."""
    df = pd.read_csv(Path(data_dir) / "raw" / "mammographic_masses.data", header=None,
                     names=_MAMMO_COLS, na_values="?").apply(pd.to_numeric, errors="coerce")
    df = df[df["severity"].notna()].reset_index(drop=True)
    y = df["severity"].astype(int).to_numpy()
    sens = pd.Series(np.where(df["age"] >= 60, "age>=60", "age<60"), name="age_group").astype("object")
    return df.drop(columns=["severity"]), y, sens


_BCW_COLS = ["id", "clump", "cell_size", "cell_shape", "adhesion", "epithelial",
             "bare_nuclei", "chromatin", "nucleoli", "mitoses", "class"]


def load_bcw(data_dir: str | Path = "data/bcw") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Breast Cancer Wisconsin (Original). Target: malignant (class==4). No protected attribute."""
    df = pd.read_csv(Path(data_dir) / "raw" / "breast-cancer-wisconsin.data", header=None,
                     names=_BCW_COLS, na_values="?")
    y = (df["class"] == 4).astype(int).to_numpy()
    X = df.drop(columns=["id", "class"]).apply(pd.to_numeric, errors="coerce")
    return X, y, pd.Series(["all"] * len(y), name="none").astype("object")


def load_spectf(data_dir: str | Path = "data/spectf") -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """SPECTF heart (cardiac SPECT diagnosis). Target: abnormal (first column). No protected attribute."""
    parts = [pd.read_csv(Path(data_dir) / "raw" / f, header=None) for f in ("SPECTF.train", "SPECTF.test")]
    df = pd.concat(parts, ignore_index=True)
    y = df.iloc[:, 0].astype(int).to_numpy()
    X = df.iloc[:, 1:].copy()
    X.columns = [f"f{i}" for i in range(X.shape[1])]
    return X, y, pd.Series(["all"] * len(y), name="none").astype("object")


def load_diabetes130(data_dir: str | Path = "data/diabetes130",
                     params: dict | None = None) -> tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """Diabetes 130-US hospitals. Target: early readmission (<30 days). Protected: race.

    `params` (from config `dataset_params.diabetes130`, covered by the calibration hash):
      n_target: subsample size, or None for the full cohort (~101,763 post gender-filter);
      subsample_seed: RNG seed for the subsample;
      stratify: "outcome" (the v1 behaviour) or "outcome_race" (joint, preserves both).
    Defaults reproduce the v1 submission exactly: n_target=6000, seed 20260626,
    outcome-only stratification."""
    raw = Path(data_dir) / "raw" / "dataset_diabetes" / "diabetic_data.csv"
    if not raw.exists():
        raw = next((Path(data_dir) / "raw").rglob("diabetic_data.csv"))
    df = pd.read_csv(raw, na_values="?", low_memory=False)
    df = df[df["gender"] != "Unknown/Invalid"].reset_index(drop=True)
    y_full = (df["readmitted"] == "<30").astype(int)
    num = ["time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
           "number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses",
           "admission_type_id", "discharge_disposition_id", "admission_source_id"]
    X = df[num].apply(pd.to_numeric, errors="coerce").copy()
    ord_map = {"None": 0, "Norm": 1, ">7": 2, ">8": 3, ">200": 1, ">300": 2}
    X["a1c"] = df["A1Cresult"].map(ord_map).fillna(0)
    X["max_glu"] = df["max_glu_serum"].map(ord_map).fillna(0)
    X["change"] = (df["change"] == "Ch").astype(int)
    X["diabetes_med"] = (df["diabetesMed"] == "Yes").astype(int)
    meds = [c for c in df.columns if c in (
        "metformin", "insulin", "glipizide", "glyburide", "pioglitazone", "rosiglitazone",
        "glimepiride", "repaglinide", "nateglinide", "acarbose")]
    X["n_meds_active"] = (df[meds] != "No").sum(axis=1)
    race = df["race"].fillna("Unknown").astype("object")
    p = params or {}
    n_target = p.get("n_target", 6000)
    # Deterministic stratified subsample (skipped when n_target is None = full cohort).
    # v1 stratified by outcome only, which preserves prevalence but leaves the race
    # distribution to chance; "outcome_race" stratifies the joint strata.
    if n_target is not None and len(X) > n_target:
        rng = np.random.RandomState(int(p.get("subsample_seed", 20260626)))
        strata = (y_full.values if p.get("stratify", "outcome") == "outcome"
                  else np.array([f"{yy}|{rr}" for yy, rr in zip(y_full.values, race.values)]))
        idx = (pd.Series(range(len(X))).groupby(strata, group_keys=False)
               .apply(lambda s: s.sample(n=max(1, int(round(len(s) * n_target / len(X)))),
                                          random_state=rng)).to_numpy())
        X, y_full, race = X.iloc[idx].reset_index(drop=True), y_full.iloc[idx], race.iloc[idx]
    return X.reset_index(drop=True), y_full.to_numpy(), pd.Series(race.values, name="race")


LOADERS = {
    "cleveland": load_cleveland, "pima": load_pima, "ilpd": load_ilpd,
    "heartfailure": load_heartfailure, "wdbc": load_wdbc,
    "statlogheart": load_statlogheart, "haberman": load_haberman, "hepatitis": load_hepatitis,
    "mammographic": load_mammographic, "bcw": load_bcw, "spectf": load_spectf,
    "diabetes130": load_diabetes130,
}


def load(name: str, data_dir: str | None = None, params: dict | None = None):
    """Load a dataset. `params` (per-dataset dict from config `dataset_params`) is passed
    to loaders that accept it; passing params for a loader that takes none is an error we
    want loud, not silent — it would mean a config knob that does nothing."""
    fn = LOADERS[name]
    args = [data_dir] if data_dir else []
    if params is not None:
        return fn(*args, params=params)
    return fn(*args)
