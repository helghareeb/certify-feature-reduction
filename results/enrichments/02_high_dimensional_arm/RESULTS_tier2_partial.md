# RESULTS — Tier 2 (PARTIAL): high-dimensional boundary arm — `arrhythmia` + `prostate_ge`

**Run:** second compute node · **2026-08-13 ~22:35 AST** · per `the partial Tier 2 request.md` (ship what's on
disk now; do not disturb the running `arcene` job). This is a **read of results already computed**; no job
was paused, and `arcene`/`gli85` remain queued to fold in when they land.

## Scope of this partial
Two of the four boundary datasets, both **validated, 30 reps**, exactly as run:

| dataset | p (features) | n | budget arms run | ranker × classifier grid | calib_sha256 |
|---|--:|--:|---|---|---|
| `arrhythmia` | **279** | 452 | **k-grid** {1,2,4,8,16,32,64,128,256} **and fracs** {0.25,0.33,0.5,0.75,1.0} | 3×3 (l1_logistic/mutual_info/rf_importance × gb/logistic/rf) | `6cbf6ff6…4e93dd` |
| `prostate_ge` | **5,966** | 102 | **k-grid** {1,2,4,8,16,32,64,128,256}; frac=1.0 baseline | 3×3 | `eea1cc34…f25f54e` |

Together with the existing paper's **p=44** clinical sets, this already spans **two orders of magnitude
(44 → 279 → 5,966)**. `arcene` (10,000) and `gli85` (22,283) *extend* the boundary; they do not create it.

## Headline — the harm from reduction is a function of p

**AUROC Δ vs full-feature baseline** (mean over the 3 rankers; k-budget arm):

### `arrhythmia` (p=279) — aggressive reduction is costly
| k | gb | logistic | rf |
|--:|--:|--:|--:|
| 1 | −0.2959 | −0.2273 | −0.3094 |
| 2 | −0.2307 | −0.1671 | −0.2437 |
| 4 | −0.1710 | −0.0956 | −0.1657 |
| 8 | −0.1140 | −0.0411 | −0.0924 |
| 16 | −0.0738 | −0.0059 | −0.0482 |
| 32 | −0.0457 | +0.0098 | −0.0278 |
| 64 | −0.0243 | +0.0152 | −0.0076 |
| 128 | −0.0034 | +0.0075 | +0.0030 |
| 256 | +0.0005 | +0.0025 | +0.0010 |

At p=279 a tight budget hurts sharply (k=1: −0.23 to −0.31 AUROC), the harm decays monotonically with k,
and by k≥128 it is negligible. Logistic regression is the most reduction-tolerant (slightly *better* at
moderate k); tree ensembles pay the most for small budgets.

### `prostate_ge` (p=5,966) — reduction is neutral-to-beneficial
| k | gb | logistic | rf |
|--:|--:|--:|--:|
| 1 | −0.0577 | −0.0270 | −0.0447 |
| 2 | −0.0303 | −0.0060 | −0.0066 |
| 4 | −0.0185 | +0.0081 | +0.0102 |
| 8 | −0.0094 | +0.0105 | +0.0183 |
| 16 | −0.0065 | +0.0070 | +0.0201 |
| 32 | −0.0040 | +0.0053 | +0.0195 |
| 64 | −0.0037 | +0.0061 | +0.0194 |
| 128 | −0.0031 | +0.0022 | +0.0177 |
| 256 | −0.0034 | +0.0031 | +0.0153 |

At p≈6,000 the same aggressive cuts cost almost nothing, and for RF they **improve** AUROC by ~+0.015–0.02
across the whole k-grid — the full space is mostly noise, so selecting a few hundred features denoises it.
Only k=1 is materially harmful, and even then far less than at p=279.

**The boundary:** reduction-harm shrinks (and flips to benefit for RF) as p grows. p=44 (paper) and p=279
sit on the "reduction hurts" side; p=5,966 sits on the "reduction is safe/helpful" side.

## Selective reliability (AURC Δ vs full, k arm, mean over rankers & k)
| dataset | gb | logistic | rf | reading |
|---|--:|--:|--:|---|
| `arrhythmia` (279) | +0.0955 | +0.0596 | +0.0948 | reduction **degrades** selective reliability |
| `prostate_ge` (5,966) | +0.0126 | −0.0031 | −0.0091 | essentially **no degradation** |

Same boundary in the AURC axis: the selective-reliability penalty that the manuscript reports is present at
moderate p and vanishes at high p. (Tier 6 will re-test this penalty under a p-independent confidence.)

## Protocol-overlap check — `arrhythmia` fracs arm (AUROC Δ vs full, mean over rankers)
| frac | gb | logistic | rf |
|--:|--:|--:|--:|
| 0.25 | −0.0215 | +0.0159 | −0.0066 |
| 0.33 | −0.0133 | +0.0121 | −0.0021 |
| 0.50 | −0.0023 | +0.0073 | +0.0029 |
| 0.75 | −0.0009 | +0.0034 | +0.0009 |

The fraction-budget arm agrees with the absolute-k arm where they overlap (e.g. frac 0.25 ≈ k≈70 lands
between the k=64 and k=128 rows), confirming the two budget protocols are consistent, not contradictory.

## Note on the headline JSON
`summary_prostate_ge.headline.json` shows `NaN` mean-deltas only because its headline key is the
**most-aggressive-frac** arm, and prostate_ge was run with frac=1.0 only (k-grid is its reduction arm).
The per-cell deltas are fully populated (81/90 non-null AUROC cells, 56 material) — see the shipped CSV.

## Deliverables (this partial)
`RESULTS_tier2_partial.md` · `summary_arrhythmia.csv` · `summary_prostate_ge.csv` (full per-cell:
mean/CI/Δ/Cohen's d/paired-diff CI/Holm-p/material flags) · `tier2_partial_harm_by_k_auroc.csv` ·
`tier2_partial_arrhythmia_fracs_auroc.csv` · `DONE.md` · `MANIFEST.sha256`.
Separate artifact, not merged (R6). Numbers, not raw caches. `arcene`/`gli85` fold in when ready.
