"""Tier 8 — cross-dataset correlates of reduction harm, WITH partials and LODO (review's TIER8).
Unit = one dataset. Primary block = the 12 clinical datasets (one protocol, frac=0.25 aggressive).
High-dim block (arrhythmia/prostate_ge/arcene/gli85) appended SEPARATELY when summaries exist -- never
pooled silently (their budget protocol differs).

Harm at the most aggressive budget, two ways, each meaned over rankers x learners:
  harm_auroc = -delta(AUROC)   (drop in AUROC; positive = worse)
  harm_aurc  = +delta(AURC)    (rise in AURC; positive = worse)
Candidates: n, p, n/p, prevalence, retained-k at the aggressive budget.
For each candidate x harm: Spearman rho, p, seeded 5000-resample bootstrap CI, LODO range.
Partials (first-order Spearman): harm~n | p, harm~p | n, harm~n | retained-k.
Descriptive only at n_datasets=12 -- caveat written into RESULTS_tier8.md.
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "src"))
from nsclinfs import data, highdim_data
data.LOADERS.update(highdim_data.HIGHDIM_LOADERS)

REPO = Path(__file__).resolve().parents[0]
SEED = 20260626
CLINICAL = ["cleveland","pima","ilpd","heartfailure","wdbc","statlogheart",
            "haberman","hepatitis","mammographic","bcw","spectf","diabetes130"]
HIGHDIM = {"arrhythmia": REPO/"results/highdim/summary_arrhythmia.csv",
           "prostate_ge": REPO/"results/highdim/summary_prostate_ge.csv",
           "arcene": REPO/"results/highdim/summary_arcene.csv",
           "gli85": REPO/"results/highdim/summary_gli85.csv"}


def harm_row(df, ds, aggressive):
    """aggressive = ('frac', 0.25) or ('k', 1). Return harm_auroc, harm_aurc, retained_k."""
    bt, bv = aggressive
    def h(outcome):
        sel = df[(df.dataset == ds) & (df.outcome == outcome) & (df.budget_type == bt)]
        sel = sel[sel.frac == bv] if bt == "frac" else sel[sel.k_features == bv]
        return sel.delta.mean(), sel.k_features.dropna().astype(float).mean()
    da, k = h("auroc"); du, _ = h("aurc")
    return -da, du, k   # harm-oriented: positive = worse


def spearman_ci(x, y, seed=SEED, B=5000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rho, p = stats.spearmanr(x, y)
    rng = np.random.RandomState(seed); n = len(x); bs = []
    for _ in range(B):
        idx = rng.randint(0, n, n)
        if len(np.unique(x[idx])) > 1 and len(np.unique(y[idx])) > 1:
            bs.append(stats.spearmanr(x[idx], y[idx]).statistic)
    lo, hi = np.percentile(bs, [2.5, 97.5]) if bs else (np.nan, np.nan)
    return float(rho), float(p), float(lo), float(hi)


def lodo(x, y, labels):
    x, y = np.asarray(x, float), np.asarray(y, float)
    out = []
    for i in range(len(x)):
        m = np.ones(len(x), bool); m[i] = False
        out.append((labels[i], round(float(stats.spearmanr(x[m], y[m]).statistic), 3)))
    vals = [v for _, v in out]
    return min(vals), max(vals), out


def partial_spearman(x, y, z):
    """First-order partial Spearman of x,y controlling z. df = n-3 for the p-value."""
    rxy = stats.spearmanr(x, y).statistic
    rxz = stats.spearmanr(x, z).statistic
    ryz = stats.spearmanr(y, z).statistic
    denom = np.sqrt((1 - rxz**2) * (1 - ryz**2))
    rp = (rxy - rxz * ryz) / denom if denom > 0 else np.nan
    n = len(x); dfree = n - 3
    if np.isfinite(rp) and abs(rp) < 1 and dfree > 0:
        t = rp * np.sqrt(dfree / (1 - rp**2)); pval = 2 * stats.t.sf(abs(t), dfree)
    else:
        pval = np.nan
    return float(rp), float(pval)


def build_block(summary_df, datasets, aggressive, label):
    rows = []
    for ds in datasets:
        X, y, _ = data.load(ds)
        ha, hu, k = harm_row(summary_df, ds, aggressive)
        rows.append({"dataset": ds, "block": label, "n": len(y), "p": X.shape[1],
                     "n_over_p": len(y) / X.shape[1], "prevalence": float(np.mean(y)),
                     "retained_k_aggr": float(k), "harm_auroc": ha, "harm_aurc": hu})
    return pd.DataFrame(rows)


# ---- primary: 12 clinical datasets, frac=0.25 aggressive ----
main = pd.read_csv(REPO/"results/summary.csv", comment="#")
clin = build_block(main, CLINICAL, ("frac", 0.25), "clinical")
clin.to_csv(REPO/"results/tier8_correlates_clinical.csv", index=False)
print("=== clinical block (n_datasets=%d), harm at frac=0.25 ===" % len(clin))
print(clin.round(4).to_string(index=False))

CANDS = ["n", "p", "n_over_p", "prevalence", "retained_k_aggr"]
report = {"n_datasets": len(clin), "aggressive_budget": "frac=0.25", "correlations": {}, "partials": {}}
for harm in ["harm_auroc", "harm_aurc"]:
    report["correlations"][harm] = {}
    print(f"\n--- {harm} vs candidates (Spearman rho [95% boot CI], p; LODO range) ---")
    for c in CANDS:
        rho, p, lo, hi = spearman_ci(clin[c], clin[harm])
        lmin, lmax, _ = lodo(clin[c].values, clin[harm].values, clin.dataset.tolist())
        report["correlations"][harm][c] = {"rho": round(rho,3), "p": round(p,4),
                                           "ci95": [round(lo,3), round(hi,3)],
                                           "lodo_min": lmin, "lodo_max": lmax}
        print(f"  {c:16s} rho={rho:+.3f} [{lo:+.3f},{hi:+.3f}] p={p:.4f}  LODO[{lmin:+.3f},{lmax:+.3f}]")
    # partials (the point)
    rn_p, pn_p = partial_spearman(clin[harm], clin["n"], clin["p"])
    rp_n, pp_n = partial_spearman(clin[harm], clin["p"], clin["n"])
    rn_k, pn_k = partial_spearman(clin[harm], clin["n"], clin["retained_k_aggr"])
    report["partials"][harm] = {
        "harm_vs_n_control_p": {"rho": round(rn_p,3), "p": round(pn_p,4)},
        "harm_vs_p_control_n": {"rho": round(rp_n,3), "p": round(pp_n,4)},
        "harm_vs_n_control_k": {"rho": round(rn_k,3), "p": round(pn_k,4)}}
    print(f"  PARTIAL {harm} vs n | p : rho={rn_p:+.3f} p={pn_p:.4f}")
    print(f"  PARTIAL {harm} vs p | n : rho={rp_n:+.3f} p={pp_n:.4f}")
    print(f"  PARTIAL {harm} vs n | k : rho={rn_k:+.3f} p={pn_k:.4f}")

# ---- secondary: high-dim block, appended separately if summaries exist ----
hd_present = {ds: fn for ds, fn in HIGHDIM.items() if Path(fn).exists()}
if hd_present:
    hd_rows = []
    for ds, fn in hd_present.items():
        df = pd.read_csv(fn, comment="#")
        aggr = ("k", 1)  # high-dim aggressive = smallest k (prostate_ge/arcene/gli85 have no frac<1)
        X, y, _ = data.load(ds)
        ha, hu, k = harm_row(df, ds, aggr)
        hd_rows.append({"dataset": ds, "block": "highdim", "n": len(y), "p": X.shape[1],
                        "n_over_p": len(y)/X.shape[1], "prevalence": float(np.mean(y)),
                        "retained_k_aggr": float(k), "harm_auroc": ha, "harm_aurc": hu})
    hd = pd.DataFrame(hd_rows)
    hd.to_csv(REPO/"results/tier8_correlates_highdim.csv", index=False)
    report["highdim_block"] = {"n_datasets": len(hd), "note": "aggressive=k:1; NOT pooled with clinical"}
    print(f"\n=== high-dim block (n_datasets={len(hd)}, aggressive=k:1, NOT pooled) ===")
    print(hd.round(4).to_string(index=False))
else:
    report["highdim_block"] = "pending arcene/gli85 (arrhythmia/prostate_ge use k-arm; folded at Tier-8 turn)"
    print("\n(high-dim block deferred: waiting on arcene/gli85 for the complete 4-set block)")

json.dump(report, open(REPO/"results/tier8_report.json", "w"), indent=2)
print("\nWROTE results/tier8_correlates_clinical.csv + tier8_report.json")
