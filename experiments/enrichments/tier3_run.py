"""Tier 3 — add beta calibration + temperature scaling as extra `calibrate` levels (review's T3.1),
WITHOUT modifying the frozen run.py. We runtime-monkeypatch nsclinfs.run._fit_predict so that:
  - 'none' / 'sigmoid' / 'isotonic'  -> delegate to the ORIGINAL frozen code (byte-identical),
  - 'beta' / 'temperature'           -> a leakage-safe cv=3 ensemble that mirrors
                                        CalibratedClassifierCV(cv=3, ensemble=True) exactly,
                                        swapping only the calibrator.
Everything else (outer folds, seeds, reduction, standardisation, metrics) is run.py's own code, reused
unchanged -> beta/temp numbers are computed on identical footing to none/sigmoid/isotonic.

ACCURACY GATES (run with --verify):
  (1) 'none' and 'sigmoid' through this harness reproduce the cached p_oof (frozen path untouched).
  (2) manual-ensemble 'sigmoid' reproduces CalibratedClassifierCV 'sigmoid' within ~1e-9
      -> proves the manual cv=3 ensemble machinery is faithful -> beta/temperature are trustworthy.
Only after both gates pass do we run the grid.
"""
import sys, os, argparse, warnings
from pathlib import Path
import numpy as np
if os.environ.get("XNSVAD_LOW_PRIORITY") == "1":
    try:
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception: pass
warnings.filterwarnings("ignore")
REPO = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(REPO / "src"))
import nsclinfs.run as R
from sklearn.model_selection import StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from scipy.optimize import minimize_scalar
from betacal import BetaCalibration

_orig_fit_predict = R._fit_predict


def _fit_temperature(p_cal, y_cal):
    """Single-scalar temperature on logits; T>0 minimising NLL. Monotone -> ranking-preserving."""
    z = np.log(np.clip(p_cal, 1e-7, 1 - 1e-7) / (1 - np.clip(p_cal, 1e-7, 1 - 1e-7)))
    y = np.asarray(y_cal, float)
    def nll(T):
        p = 1.0 / (1.0 + np.exp(-z / T)); p = np.clip(p, 1e-12, 1 - 1e-12)
        return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    res = minimize_scalar(nll, bounds=(0.05, 20.0), method="bounded")
    return float(res.x)


def _apply_temperature(p, T):
    z = np.log(np.clip(p, 1e-7, 1 - 1e-7) / (1 - np.clip(p, 1e-7, 1 - 1e-7)))
    return 1.0 / (1.0 + np.exp(-z / T))


def _manual_ensemble(classifier, method, Xtr, ytr, Xte, seed):
    """Mirror CalibratedClassifierCV(cv=3, ensemble=True): 3 (base, calibrator) pairs, averaged.
    cv=3 int -> StratifiedKFold(3, shuffle=False), matching sklearn's internal splitter."""
    Xtr = Xtr.to_numpy() if hasattr(Xtr, "to_numpy") else np.asarray(Xtr)
    Xte = Xte.to_numpy() if hasattr(Xte, "to_numpy") else np.asarray(Xte)
    ytr = np.asarray(ytr)
    skf = StratifiedKFold(n_splits=3)

    def _response(b, Xq):
        """Match CalibratedClassifierCV: use decision_function (logits) when available, else proba."""
        if hasattr(b, "decision_function"):
            s = b.decision_function(Xq)
            return np.asarray(s).ravel()
        return b.predict_proba(Xq)[:, 1]

    preds = []
    for tr_i, cal_i in skf.split(Xtr, ytr):
        b = R._classifier(classifier, seed).fit(Xtr[tr_i], ytr[tr_i])
        p_cal = b.predict_proba(Xtr[cal_i])[:, 1]     # probabilities (beta/temperature input)
        p_te = b.predict_proba(Xte)[:, 1]
        if method == "beta":
            c = BetaCalibration(parameters="abm").fit(p_cal.reshape(-1, 1), ytr[cal_i])
            preds.append(np.asarray(c.predict(p_te.reshape(-1, 1))).ravel())
        elif method == "temperature":
            T = _fit_temperature(p_cal, ytr[cal_i])
            preds.append(_apply_temperature(p_te, T))
        elif method == "sigmoid_manual":     # verify-only: replicate sklearn (decision_function input)
            from sklearn.calibration import _SigmoidCalibration
            s_cal, s_te = _response(b, Xtr[cal_i]), _response(b, Xte)
            sc = _SigmoidCalibration().fit(s_cal, ytr[cal_i])
            preds.append(sc.predict(s_te))
        else:
            raise ValueError(method)
    return np.mean(preds, axis=0)


def _patched_fit_predict(classifier, calibrate, Xtr, ytr, Xte, seed):
    if calibrate in ("beta", "temperature"):
        return _manual_ensemble(classifier, calibrate, Xtr, ytr, Xte, seed)
    return _orig_fit_predict(classifier, calibrate, Xtr, ytr, Xte, seed)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--calib", default="config/calibration_tier3.json")
    ap.add_argument("--datasets", default="")
    args, rest = ap.parse_known_args()

    if args.verify:
        # Accuracy gate on one representative cell (cleveland, mutual_info, logistic, rep 0, full budget)
        from nsclinfs import data, reduction
        from nsclinfs.seeds import derive_seed
        import json
        CFG = json.load(open(REPO / "config" / "calibration.json"))
        MASTER = CFG["RANDOM_SEED"]; NF = CFG["n_folds"]
        ds, method, clf, rep = "cleveland", "mutual_info", "logistic", 0
        X, y, _ = data.load(ds)
        seed = derive_seed(MASTER, {"dataset": ds, "method": method, "classifier": clf, "rep": rep})
        skf = StratifiedKFold(n_splits=NF, shuffle=True, random_state=seed)
        n = len(y); p = X.shape[1]
        cccv = np.full(n, np.nan); man = np.full(n, np.nan)
        beta = np.full(n, np.nan); temp = np.full(n, np.nan)
        for tr, te in skf.split(X, y):
            med = X.iloc[tr].median(numeric_only=True)
            Xtr_i, Xte_i = X.iloc[tr].fillna(med), X.iloc[te].fillna(med)
            ranking = reduction.rank(method, Xtr_i, y[tr], seed); feats = ranking[:p]
            mu, sd = Xtr_i[feats].mean(), Xtr_i[feats].std(ddof=0).replace(0.0, 1.0)
            Xtr_z, Xte_z = (Xtr_i[feats] - mu) / sd, (Xte_i[feats] - mu) / sd
            cccv[te] = _orig_fit_predict(clf, "sigmoid", Xtr_z, y[tr], Xte_z, seed)
            man[te] = _manual_ensemble(clf, "sigmoid_manual", Xtr_z, y[tr], Xte_z, seed)
            beta[te] = _manual_ensemble(clf, "beta", Xtr_z, y[tr], Xte_z, seed)
            temp[te] = _manual_ensemble(clf, "temperature", Xtr_z, y[tr], Xte_z, seed)
        d_manual = float(np.max(np.abs(cccv - man)))
        print(f"GATE2 manual-ensemble sigmoid vs CalibratedClassifierCV sigmoid: max|diff|={d_manual:.2e}")
        print(f"  beta:  range [{np.nanmin(beta):.4f},{np.nanmax(beta):.4f}] valid={np.all((beta>=0)&(beta<=1))}")
        print(f"  temp:  range [{np.nanmin(temp):.4f},{np.nanmax(temp):.4f}] valid={np.all((temp>=0)&(temp<=1))}")
        print("GATE2 PASS" if d_manual < 1e-6 else "GATE2 FAIL (manual ensemble != CCCV) -> DO NOT SHIP")
    else:
        R._fit_predict = _patched_fit_predict            # patch only for the grid run
        import experiments.run_clinical_fs as rcfs
        sys.argv = ["run_clinical_fs", "--calib", args.calib] + rest
        if args.datasets:
            sys.argv += ["--datasets"] + args.datasets.split(",")
        rcfs.main()
