"""Enrichment #7: is the harm mechanistically linked to ranking instability?

For every (dataset, ranker) pair, recompute the per-fold feature rankings exactly as the
grid does -- same derive_seed(master, {dataset, method, classifier, rep}) seeds, same
StratifiedKFold, same in-fold median imputation, same rank() call -- across all 30
repetitions x 5 folds = 150 rankings, and measure the stability of the selected top-k set
(pairwise Jaccard across all 150 selections) at the dataset's most aggressive-budget k and
at k=4 (the matched-k anchor). Then correlate per-dataset stability with the AURC harm.

Rankings are classifier-independent, so we compute them once per (dataset, ranker) using
the 'logistic' seed stream -- NOTE this reproduces the grid's rankings for the logistic
cells exactly, and is statistically identical (not bitwise) for rf/gb cells, whose seeds
differ. This is a mechanism analysis, not a reproduction claim, and the manuscript states
the same.

Cost: rankings only, no model fits. Persists every selection to
results/cache/rankings/<dataset>__<method>.parquet (hash-stamped) so the analysis re-runs
from cache. Emits results/ranking_stability.json + paper/figures/stability_harm.pdf.

    PYTHONPATH=src python experiments/ranking_stability.py [--workers 6]
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def rankings_for(args) -> tuple[str, str, list[list[str]]]:
    ds, method, calib = args
    from sklearn.model_selection import StratifiedKFold

    from nsclinfs import data as dataload
    from nsclinfs import reduction
    from nsclinfs.seeds import derive_seed

    X, y, _ = dataload.load(ds, params=calib.get("dataset_params", {}).get(ds))
    sels = []
    for rep in range(int(calib["REPS"])):
        seed = derive_seed(calib["RANDOM_SEED"], {"dataset": ds, "method": method,
                                                  "classifier": "logistic", "rep": rep})
        skf = StratifiedKFold(n_splits=int(calib["n_folds"]), shuffle=True, random_state=seed)
        for tr, _te in skf.split(X, y):
            med = X.iloc[tr].median(numeric_only=True)
            sels.append(reduction.rank(method, X.iloc[tr].fillna(med), y[tr], seed))
    return ds, method, sels


def jaccard_topk(rankings: list[list[str]], k: int) -> float:
    sets = [frozenset(r[:k]) for r in rankings]
    vals = [len(a & b) / len(a | b) for a, b in combinations(sets, 2)]
    return float(np.mean(vals))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", default="config/calibration.json")
    ap.add_argument("--summary", default="results/summary.csv")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    calib = json.loads((ROOT / a.calib).read_text())

    from scipy.stats import spearmanr

    from nsclinfs.hashing import CALIB_HASH_KEY, assert_single_hash, content_hash
    from nsclinfs.reduction import retained_k
    chash = content_hash(calib)

    cache_dir = ROOT / "results/cache/rankings"
    cache_dir.mkdir(parents=True, exist_ok=True)
    jobs, cached = [], {}
    for ds in calib["datasets"]:
        for method in calib["reduction_methods"]:
            f = cache_dir / f"{ds}__{method}.parquet"
            if f.exists():
                df = pd.read_parquet(f)
                if df.attrs.get(CALIB_HASH_KEY, df[CALIB_HASH_KEY].iloc[0]) == chash:
                    cached[(ds, method)] = [list(r) for r in df["ranking"]]
                    continue
            jobs.append((ds, method, calib))
    print(f"[stability] {len(cached)} cached, {len(jobs)} to compute on {a.workers} workers")
    if jobs:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for ds, method, sels in ex.map(rankings_for, jobs):
                pd.DataFrame({"ranking": [list(s) for s in sels],
                              CALIB_HASH_KEY: chash}).to_parquet(
                    cache_dir / f"{ds}__{method}.parquet", index=False)
                cached[(ds, method)] = sels
                print(f"[stability] {ds}/{method}: {len(sels)} rankings", flush=True)

    # stability at the aggressive-budget k and at the matched anchor k=4
    s = pd.read_csv(ROOT / a.summary, comment="#")
    assert_single_hash(s[CALIB_HASH_KEY])
    frac_arm = s[s["budget_type"] == "frac"] if "budget_type" in s.columns else s
    fmin = frac_arm["frac"].min()
    aggr = frac_arm[(frac_arm["frac"] == fmin) & (frac_arm["outcome"] == "aurc")
                    & (frac_arm["calibrate"] == "none")]
    harm = aggr.groupby("dataset")["delta"].mean()
    # Per-(dataset, ranker) harm. The per-dataset mean above collapses the three rankers,
    # leaving only 12 points to test "the harm is selection noise" on. Each ranker has its
    # own stability AND its own harm, so the (dataset, ranker) pair is the natural unit and
    # gives 36. See the within-dataset variant below for why the pooled number is not enough.
    harm_by_ranker = aggr.groupby(["dataset", "method"])["delta"].mean()

    out, rows, pair_rows = {}, [], []
    for ds in calib["datasets"]:
        p = len(cached[(ds, calib["reduction_methods"][0])][0])
        k_aggr = retained_k(fmin, p)
        per_method = {}
        for method in calib["reduction_methods"]:
            sels = cached[(ds, method)]
            j_aggr = jaccard_topk(sels, k_aggr)
            per_method[method] = {
                f"jaccard_k{k_aggr}": round(j_aggr, 4),
                "jaccard_k4": round(jaccard_topk(sels, min(4, p - 1)), 4) if p > 1 else 1.0,
            }
            h_pair = harm_by_ranker.get((ds, method), np.nan)
            if np.isfinite(h_pair):
                per_method[method]["aurc_harm"] = round(float(h_pair), 4)
                pair_rows.append((ds, method, j_aggr, float(h_pair)))
        mean_j = float(np.mean([m[f"jaccard_k{k_aggr}"] for m in per_method.values()]))
        out[ds] = {"p": p, "k_aggressive": k_aggr, "per_method": per_method,
                   "mean_jaccard_aggressive": round(mean_j, 4),
                   "aurc_harm": round(float(harm.get(ds, np.nan)), 4)}
        rows.append((ds, mean_j, float(harm.get(ds, np.nan))))

    df = pd.DataFrame(rows, columns=["dataset", "stability", "harm"]).dropna()
    r, pv = spearmanr(df["stability"], df["harm"])
    out["_correlation"] = {"spearman_stability_vs_harm": round(float(r), 3),
                           "p": round(float(pv), 4), "n": int(len(df))}

    # The same test at the (dataset, ranker) level. Two versions, because they answer
    # different objections: POOLED asks whether stability tracks harm anywhere in the
    # study; WITHIN-DATASET ranks both variables inside each dataset first, so the dataset
    # main effect -- which is what actually drives harm -- can neither manufacture nor mask
    # a stability association. A noise mechanism predicts a NEGATIVE rho in both (unstable
    # selection => more harm); anything >= 0 is evidence against it.
    pf = pd.DataFrame(pair_rows, columns=["dataset", "method", "stability", "harm"]).dropna()
    r_p, pv_p = spearmanr(pf["stability"], pf["harm"])
    w = pf[pf.groupby("dataset")["dataset"].transform("size") >= 3].copy()
    w["rj"] = w.groupby("dataset")["stability"].rank()
    w["rh"] = w.groupby("dataset")["harm"].rank()
    r_w, pv_w = spearmanr(w["rj"], w["rh"])
    # The within-dataset p above is anticonservative: 36 rows, but only 12 INDEPENDENT
    # blocks. The valid null permutes harm among the three rankers inside each dataset,
    # which is exactly the exchangeability being assumed. Seeded, so it is reproducible.
    rng = np.random.default_rng(int(calib["RANDOM_SEED"]))
    grps = [g for _, g in w.groupby("dataset")]
    obs = float(r_w)
    n_perm, hits, hits_one = 20000, 0, 0
    for _ in range(n_perm):
        rj, rh = [], []
        for g in grps:
            rj += list(g["stability"].rank())
            rh += list(pd.Series(rng.permutation(g["harm"].to_numpy())).rank())
        rp = float(spearmanr(rj, rh)[0])
        hits += abs(rp) >= abs(obs)
        hits_one += rp <= obs
    out["_correlation_by_ranker"] = {
        "pooled": {"spearman_stability_vs_harm": round(float(r_p), 3),
                   "p": round(float(pv_p), 4), "n": int(len(pf))},
        "within_dataset": {"spearman_stability_vs_harm": round(float(r_w), 3),
                           "p_parametric_ANTICONSERVATIVE": round(float(pv_w), 4),
                           "p_block_permutation_two_sided": round(hits / n_perm, 4),
                           "p_block_permutation_one_sided": round(hits_one / n_perm, 4),
                           "n_pairs": int(len(w)), "n_blocks": len(grps),
                           "n_permutations": n_perm},
        "note": ("Negative rho is the direction the selection-noise hypothesis PREDICTS "
                 "(less stable -> more harm). The within-dataset trend is therefore not "
                 "evidence against that hypothesis; it is a weak, non-significant trend "
                 "toward it, and it is confounded with ranker quality. Section 4.7 rests "
                 "the claim on the exact-k arm and on the most-harmed datasets being among "
                 "the most stable, not on this correlation."),
    }
    (ROOT / "results/ranking_stability.json").write_text(json.dumps(out, indent=2) + "\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    ax.scatter(df["stability"], df["harm"], color="#2c6fbb")
    for _, row in df.iterrows():
        ax.annotate(row["dataset"], (row["stability"], row["harm"]), fontsize=6, alpha=0.75,
                    xytext=(3, 3), textcoords="offset points")
    ax.axhline(0, color="grey", lw=0.6, ls=":")
    ax.set_xlabel("top-$k$ selection stability (mean pairwise Jaccard, aggressive budget)")
    ax.set_ylabel("AURC penalty at the aggressive budget")
    ax.set_title(f"Selection stability vs.\\ harm (Spearman $\\rho={r:+.2f}$)", fontsize=9)
    fig.tight_layout()
    fig.savefig(ROOT / "paper/figures/stability_harm.pdf")
    print(json.dumps(out["_correlation"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
