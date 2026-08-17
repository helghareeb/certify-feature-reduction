# T2.1 — high-dimensional (p ≫ 44) dataset shortlist for your sign-off

**Run:** second compute node · **2026-08-13 ~13:35 AST** · Tier-2 acquisition only (no loaders written, no `config` datasets extended, as pre-specified). **Reporting, then stopping — dataset choice is yours.**

All candidates **downloaded, sha256'd, and n/p/class-balance verified here** (files under `<high-dimensional data directory>\`, not synced; raw not shipped). All are genuinely **binary** (no binarizing needed).

## Verified candidates (ranked; best first)
| # | dataset | n | p | class balance | licence | size | sha256 (first 16) |
|--:|---|--:|--:|---|---|--:|---|
| 1 | **Arcene** (mass-spec, cancer vs normal) | 200 | **10,000** | 112 / 88 (56/44) | ✅ **CC BY 4.0** (UCI) | 1.9 MB (.mat) / 8.6 MB (UCI zip) | 779d678207b9a8c0 (.mat) · c7a40e39edf23a9b (UCI zip) |
| 2 | **Prostate-GE** (prostate tumor vs normal) | 102 | 5,966 | 50 / 52 (**balanced**) | ⚠️ unconfirmed | 1.5 MB | 050b598534dbc662 |
| 3 | **SMK-CAN-187** (lung cancer vs control) | 187 | **19,993** | 90 / 97 (**balanced**) | ⚠️ unconfirmed | 11.9 MB | 96ff62a9dad001b4 |
| 4 | **GLI-85** (glioma grade) | 85 | **22,283** | 26 / 59 (31/69) | ⚠️ unconfirmed | 8.7 MB | c1170b0b7ef8dc8e |
| 5 | **ALLAML** (leukemia ALL vs AML) | 72 | 7,129 | 47 / 25 (65/35) | ⚠️ unconfirmed | 3.6 MB | 068afe0fe1021932 |
| 6 | Colon/Alon (tumor vs normal) | 62 | 2,000 | 40 / 22 (65/35) | ⚠️ unconfirmed | 36 KB | ffcdeba03eb67cec |

Full record: `t2_verify.json` (all fields + full sha256 + source URLs). Sources: Arcene = UCI id 167 (CC BY 4.0) + OpenML id 1458; #2–6 = scikit-feature `.mat` mirror (direct, no wall).

## 🔴 The licence caveat (needs your ruling)
- **Only Arcene has a confirmed open licence (CC BY 4.0).** It is also the strongest technical fit (p=10,000, ~balanced, includes 3,000 injected probe features — ideal for a feature-selection stress test) and a recognized NIPS-2003 benchmark.
- **#2–6 are directly downloadable but the *data* licence is not explicitly declared** (the scikit-feature repo's *code* is GPL-2.0; the microarray data derive from public GEO studies / original papers). For publication I'd recommend citing the **original studies** and/or an **OpenML mirror** (where a licence field exists) rather than the GitHub repo. Flagging, not deciding.
- Clean-licence UCI alternatives exist but are poor fits: **p53 Mutants** (CC BY 4.0, p=5,408, but <1% positive and ~527 MB) and **Dorothea** (CC BY 4.0, p=100,000, ~1:9 imbalance, sparse-binary).

## My recommendation (yours to confirm/override)
For 3–4 datasets spanning the p≫44 regime with the cleanest defensibility:
**Arcene (p=10k, clean licence) + SMK-CAN-187 (p≈20k, balanced) + GLI-85 (p≈22k, extreme p≫n) + Prostate-GE (p≈6k, balanced)** — with the licence for the three gene-expression sets resolved to their original-study / OpenML citations before final use.

## Next (on your confirmation)
Once you pick the set, T2.2 = a timing probe (1 rep, 1 fold, 3 rankers × 3 learners, peak RSS) on ONE chosen dataset to tell us hours-vs-days before any full run — **without writing a loader/config** (I'll feed the raw X,Y to `probe_timing.py` directly). **I am not writing loaders or extending `config` until you confirm the set.**
