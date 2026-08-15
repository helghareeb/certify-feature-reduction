# REVISION_NOTES — certify-feature-reduction, SR revision round 1 (2026-08-11 → deadline 2026-08-24)

> Per-paper working ledger (the `REVISION_NOTES.md` discipline from ns-fraud). Newest entries at
> the bottom of each section. The point-by-point map lives in `RESPONSE.md`; this file holds the
> engineering state, decisions, and anything that must not be lost between sessions.

## Frame

- Decision email + reviews verbatim: `paper/reviews/`. Deadline: **2026-08-24** (portal, author-confirmed).
- Branch: `revision-sr-r1` off `main`. Submitted tree: retro tag `submitted-2026-06-28`
  (= e8b93f9, the SR package commit). v1 hashes: main `1d05f19c…`, recal `82fc3197…`.
- Author decisions 2026-08-11: aggressive over-delivery; FULL grid on FULL Diabetes-130 cohort;
  CLEAN REBUILD of the whole grid under a v2 calibration; repo goes PUBLIC on resubmission day;
  the secondary compute node's 20-thread CPU authorized as deadline fallback.
- Plan of record: `C:\Users\HP\.claude-the secondary compute node\plans\shimmering-gliding-wand.md` (hub-side; do not
  cite in anything public).

## Execution state

- [x] W-A intake: reviews stored, tag cut, branch cut, RESPONSE.md + this file scaffolded
- [x] Hub records: registry.tsv / TRIAGE / DEADLINES / correspondence / tasks.tsv / PAPER_REGISTRY
- [x] Stage 0: env pin · fetch_data.py + MANIFEST · v1 cleveland spot-check
- [x] Stage 1: timing probe (probe_timing.py) → Plan A/B verdict
- [x] Stage 2: v2 code (budgets/exact-k, config plumbing, hash enforcement at 4 holes + merger,
      p_oof/nb_curves caches, diabetes130 config-driven loader, tests)
- [x] R1.1 Tier-1 reanalysis off v1 summary (zero fits) → response prose draft
- [x] Stage 3: v1 archive + v2 config freeze + tag `revision-v2-config-freeze`
- [x] Stage 4 (burn COMPLETE, 87+29+54 shards, 0 failures, ~10h via Task Scheduler): the burn (main → recal → subcheck), chunked/resumable, ≤10 workers
- [x] Stage 5: aggregated + every artifact regenerated + caches committed
- [x] Stage 6: v1-vs-v2 diff PASS (rf/gb 1e-16, logistic <=5e-5, verdicts 5265/5265); manuscript numbers rewritten (19pp, 0 err)
- [x] W-C line pass + R1.2 writing (parallel with the burn)
- [x] W-E release-scrub (flip design recorded; LICENSE/CITATION/README/AGENTS/addendum done; Code Availability rewritten) (public flip prep: CODE-scrub, LICENSE, CITATION.cff, cold-clone check,
      git-history review)
- [~] W-F (mechanical part DONE; author signature owed): AUD-0 (`audit_gate.py --write-verdict` + author signs AUD-5..10 — NO upload before),
      SR package (NO PDF, separate figs, response file, no stray .bib, empty-TEXMFHOME acid
      test), new tag, B2 backup + results_index.tsv, hub writebacks

## Engineering decisions (running log)

- 2026-08-11 — Retention rule `max(1, int(round(frac·p)))` is KEPT byte-identical (single home:
  `reduction.retained_k`), disclosed in Methods with its consequence table; "fixing" it would
  silently change k for 5 datasets. Banker's-rounding cases: 5@0.5→2, 30@0.75→22, 18@0.25→4,
  11@0.5→6, 3@0.25→1.
- 2026-08-11 — Exact-k arm k∈{1,2,4,8} inside the same rep (seeds exclude budget → pairing
  free); Holm families computed WITHIN budget_type so the submitted frac-family p_holm values
  cannot drift; equal-k compute deduped and emitted under both labels.
- 2026-08-11 — Worked example fixed a priori: mammographic × (mutual_info, logistic, none) ×
  t=0.10 (BI-RADS 4b biopsy boundary), sensitivity {0.05, 0.15}; secondary diabetes130-full at
  t=0.10 (~prevalence 0.112). Presentation thresholds live in `config/analysis.json` (own
  hash), so moving a threshold never re-burns the grid. NB at t≳0.3 on diabetes is ≈0 for both
  arms (prevalence) — the primary example deliberately avoids that regime.
- 2026-08-11 — Recal arm at full cohort ONLY if the probe clears isotonic×RF×full (the likely
  cliff); documented fallback: recal keeps n=6000 as a separately-hashed mechanism control.
- 2026-08-11 — The 6k subsample is DEMOTED to a robustness arm (subsample-agreement table);
  because of that, fixing the race-stratification bug (joint outcome×race) is safe. If any
  subsampled diabetes number were to stay headline, that decision must be revisited jointly.

## Results log

- 2026-08-11 — **R1.1 Tier-1 reanalysis complete** (`experiments/meta_analysis_k.py`, zero new
  fits, off the v1 summary). ρ(p,harm)=−0.730 REPRODUCED exactly (pipeline validated).
  Findings: ρ(k_min,harm)=**−0.797** — absolute retained-k predicts harm MORE strongly than p;
  k=1-collapse indicator ρ=+0.583 (p=0.047); excluding haberman+mammographic, ρ(p,harm)=−0.622
  at p=0.055 (n=10) — attenuated, survives directionally. Matched-k: at k=3 harm spans +0.008
  (heartfailure) to +0.068 (statlogheart) — neither p nor k alone determines harm; clean
  within-dataset dose-response on absolute k (mammographic +0.0003@k4 → +0.029@k2 → +0.070@k1).
  RESPONSE LINE: the reviewer's reading is CONFIRMED as the stronger axis, the screen is
  restated on retained-k with p as a secondary correlate, and the v2 exact-k arm (k=1 for ALL
  datasets) is the decisive test. Artifacts: results/meta_k.json + paper/meta_k_table.tex.

- 2026-08-11 — **Stage-1 probe verdict: PLAN A CONFIRMED, no cliff.** Measured on the full
  cohort (n=101,763, prevalence 0.1116, train fold 81,410): rankings mi 10.8s / rf_imp 11.9s /
  l1 0.3s; fits rf@k16 23.5s, rf@k4 5.8s, gb@k16 5.2s, logistic ≈0.1s; rf+isotonic 50.4s,
  rf+sigmoid 60.0s. Projection: diabetes main ≈13.5h + diabetes recal (FULL cohort, all 3
  calibrations) ≈9.5h + 11 small datasets ≈6h ≈ **30h single-threaded ≈ 5-6h on 6 workers**
  (8 logical cores, 16 GB here). Full grid + full-cohort recal + exact-k arm ALL fit locally
  with days of margin; the secondary compute node fallback NOT needed. `results/timing_probe.json`.
  (probe's peak-RSS readout returned 0 on this box — psutil absent and the ctypes fallback
  failed silently; memory risk judged low: 81k×16 float data is ~10 MB, forests ~100-300 MB,
  6 workers × 0.5 GB ≪ 16 GB.)

- 2026-08-11 — **Stage-0 v1 spot-check: VERDICT-LEVEL PASS, numeric drift documented.**
  Cleveland re-run under the (previously unpinned, now locked) environment: 528/540 aggregate
  rows bit-equal; 12 rows drift ≤5e-5 in means (one p_holm by 0.004). Drift is confined to
  LOGISTIC cells at fracs 0.33/0.5 on ranking-sensitive outcomes while rf/gb cells sharing the
  SAME per-fold rankings are bit-identical → the rankings reproduce exactly and the drift lives
  inside the LBFGS logistic solve (scipy/sklearn version sensitivity; v1 shipped no lock file —
  that omission is itself fixed this round). **All 540/540 material verdicts identical.**
  DECISION: proceed — the clean v2 rebuild replaces every reported number under the pinned env
  anyway; the Stage-6 invariance expectation is REVISED accordingly (rf/gb + rankings: exact;
  logistic cells: ≤1e-4 with identical verdicts). Response letter states verdict-level
  reproduction honestly, not "byte-identical".
- 2026-08-11 — **Stage 2 complete, 27/27 tests green.** v2 runner (_eval_budgets: frac + exact-k
  levels, dedupe bitwise-verified by test, k>=p skipped), Holm families per budget_type
  (isolation test passes), hash gate ENFORCED at do_aggregate/--append/figure-loader/
  meta-loader/merger, k_features+n_features+runtime_s in every row, p_oof + NB-curve caches,
  config-driven diabetes130 (joint stratification bug found by test and fixed: groupby needed a
  combined stratum key), launcher (6 workers, resumable, atomic shards) + merger (hash + dup +
  row-count asserts). matplotlib was MISSING from the venv — the v1 figures were built in some
  other env; installed + re-locked.

## The public-flip release design (decided 2026-08-11, W-E)

The repo goes public on resubmission day (author's R1.5 decision) — but `paper/reviews/`
(verbatim reviewer reports), `paper/RESPONSE.md` and this file are CONFIDENTIAL while the
paper is under review, and they are committed on `revision-sr-r1`. History rewrite is off the
table (it would break the N4 tags and every recorded SHA). Therefore, at flip time:

1. **Squash-merge `revision-sr-r1` → `main` as ONE commit that EXCLUDES** `paper/reviews/`,
   `paper/RESPONSE.md`, `paper/REVISION_NOTES.md` (they never enter main's history);
2. delete the `revision-sr-r1` branch AND the `revision-v2-config-freeze` tag **on the
   remote** (both stay in the local clone + the hub records as the private working record);
3. cut the resubmission tag on the squashed main commit;
4. THEN the author flips the repo public. Main's public history = v1 history + one clean
   revision commit; no reviewer text, no process tells.

The response-to-reviewers letter itself ships to SR as a submission file, not in the repo.

## Known defects being fixed this round (found by our own audit, not the reviewers)

1. `data.py:169` comment claims race-preserving subsample; code stratifies by outcome only.
2. `data.py:148` + `data/diabetes130/README.md` say "~12k"; code and manuscript say 6,000.
3. `assert_single_hash` is dead code while `main.tex:372-374` claims mixed-hash refusal — wire
   it at: do_aggregate, --append, make_figures._load, meta_analysis.harm_by_dataset, + merger.
4. Tests (4) all skipif-gated on Cleveland raw → fresh clone shows a hollow green. Global
   pytestmark goes; pure-metric tests must run dataless.
5. `results/summary.headline.json` `n_features: 12` is a first-dataset artifact.
6. README.md stale (5 datasets, JBI venue); PRE_REGISTRATION gets a dated addendum (never
   silently rewritten); AGENTS.md references the private hub → rewritten before the public flip.
7. No LICENSE, no CITATION.cff, no data fetch script — all owed before the public flip.

- 2026-08-11 (post-main-grid) — **v2 MAIN GRID LANDED + the decisive results.** (a) Invariance
  PASS at the strongest form: rf/gb + rankings reproduce v1 to 1e-16, logistic within the
  documented envelope, 100% verdict agreement (5,265 rows), diabetes130 moved by design
  (results/v1_v2_diff.json). (b) **Exact-k arm settles R1.1: at k=1 EVERY dataset is harmed**
  — spectf +0.0353, wdbc +0.0298, diabetes130 +0.0269, statlogheart +0.1911, cleveland +0.1784.
  Wide datasets were never intrinsically robust; fractional budgets just never took them near
  small k. v2 screen: ρ(p)=-0.709, ρ(k_min)=-0.779, LODO all-negative, bootstrap CIs exclude 0.
  (c) **Safe-budget certificate almost never passes**: only wdbc admits a certified-safe
  reduction (k=22/30); every other dataset has ≥1 materially-worse cell at every probed budget —
  the certificate, not any proxy screen, is the deliverable. (d) **Worked example (R1.3)**:
  mammographic t=0.10 → 203/961 (21%) biopsy decisions flip in the majority of paired models,
  4 true malignancies pushed below threshold; diabetes130 full cohort → 14,324/101,763 (14.1%)
  enrollment flips, 1,132 true readmissions lose the intervention. (e) **Race split**: mean flip
  rate 0.112 (Hispanic) → 0.149 (Caucasian) — NOT concentrated on minority groups here; report
  as measured. Artifacts: meta_k.json, safe_budget.json, worked_example.json + 3 new figures +
  3 new table fragments.

- 2026-08-11 (final) — **PACKAGE READY.** Response letter (3pp, generated from RESPONSE.md, no
  salutation), MANIFEST.toml + LOCAL_EXECUTION_PLAYBOOK.md authored, R6 canonicalization
  (content_hash == file_bytes == stamp, .gitattributes-guarded), AUD-0 MECHANICAL ALL-PASS,
  verdict drafted at hub AUDIT_certify-feature-reduction_2026-08-11.md with my read PASS on all six human
  gates — AUTHOR SIGNATURE PENDING (do not upload before signing; two papers shipped unsigned
  already). SR revision zip built per revision rules (NO manuscript PDF, separate figures, no
  .bib, jabbrv bundled, response PDF included): paper/certify-feature-reduction_SR_revision.zip — ACID
  PASS (0 err / 0 undef / 19pp, clean extract, TEXMFHOME hidden). REMAINING (author): 1) sign
  AUD-5..10 in the hub verdict; 2) upload the zip contents at the SR portal (manuscript source
  + separate figure PDFs + response_to_reviewers.pdf; NO main.pdf); 3) the public flip per the
  recorded design (squash-merge excluding reviews/RESPONSE/REVISION_NOTES, delete branch+freeze
  tag remotely, tag the squashed commit, flip); 4) B2: ATHAR copy when F: is next mounted.

## POLISH PLAN — EXECUTED 2026-08-12. Tier A complete; Tier B still the author's call.

**Outcome: A1–A6 all done, and the A3 sweep found four numeric defects the earlier passes
missed — three of them in numbers already quoted to the reviewers.** Every one is corrected
against the committed JSONs, and each now resolves to a key that the generator emits rather
than to a number transcribed by hand:

1. **§4.7 floor-excluded correlation was overstated.** Manuscript and response letter both
   said $\rho=-0.62$, $p=0.055$, $n=10$; `results/meta_k.json` says $-0.585$, $p=0.0754$.
   Corrected to $\rho=-0.59$, $p=0.075$ — which *strengthens* the reply to R1.1, because the
   $p$-association is then not merely attenuated but non-significant, leaving the retained
   count as what survives. The bootstrap CI for the retained count ($[-0.98,-0.32]$) is now
   quoted too.
2. **§4.7 leave-one-dataset-out range was stale v1 text.** Said "$-0.90$ to $-0.74$";
   `meta_k.json` `lodo_range` is $[-0.878,-0.712]$. Corrected to $-0.88$ to $-0.71$.
3. **§4.9 / response letter: "in one cell the subsample reversed the sign" was wrong** —
   `sign_agree` is 27 of 45, i.e. **18** sign reversals. The named cell (mutual-info × RF,
   AUROC $+0.028$ vs $-0.028$) is the largest, not the only one. Both documents now say 18 of
   45 and name that cell as the most consequential; this too strengthens R1.4's answer.
   `subsample_agreement.py` now emits `sign_reversals`, `median_abs_delta_gap`,
   `verdict_full_only_material` / `verdict_6k_only_material` (12 / 8 — confirmed, not changed)
   and `largest_sign_reversal`, so the sentence is anchored rather than counted by eye.
4. **Response letter's reproducibility bound was both too tight and contradicted by the
   committed JSON.** The letter claimed "within $5\times10^{-5}$ for logistic regression";
   the true max on any estimate or interval bound is $5.119\times10^{-5}$ — just over. Worse,
   `v1_v2_diff.json` reported `max_drift_logistic = 3.9\times10^{-3}`, because the pooled
   maximum was dominated by `p_holm`: a metric moving $10^{-5}$ moves a Wilcoxon $p$ by
   $10^{-3}$. A reader comparing letter to repo would have seen a 78× discrepancy.
   `v1_v2_diff.py` now reports `max_drift_*_metrics` and `max_drift_*_pvalues` separately
   (pooled key kept), and the letter states the honest envelope: machine precision
   ($\le1.2\times10^{-16}$) for rf/gb, within $1\times10^{-4}$ for logistic (max
   $5.1\times10^{-5}$), p-values moving at most $3.9\times10^{-3}$, all 5{,}265 verdicts
   identical.

Smaller A3 findings, all fixed: §4.3's "the robust datasets are those with many candidate
features … so a quarter still spans the signal" still argued the *retired* width claim, now
reframed onto the absolute retained count; §4.2's "silent cell" definition omitted the Brier
score that `make_figures.silent_cells` actually includes; Table `tab:newaxes` was captioned
"four new reliability axes" for a five-row table; the response letter cross-referenced the
full-cohort section as "Section 4.8" when it is **4.9**; and the Introduction's illustrative
"18 % risk" was wrapped in `\result{}`, which by MANIFEST convention marks a *regenerated*
number — unwrapped, since no code produces it.

Everything else verified clean: all 146 `\result{}` tokens were checked against
`summary.headline.json`, `new_axes_table`, `meta_k.json`, `safe_budget.json`,
`ranking_stability.json`, `worked_example.json`, `subsample_agreement.json` and a direct
streaming recount of `results/summary.csv` (per-budget means and material-worse counts at
0.75/0.5/0.33/0.25, per-learner deltas at 0.25, Diabetes-130 full-feature AUROC 0.6449 ≈ 0.65).
The dose-response monotonicity claim holds for AURC, AUROC and net benefit. No leftover
silent-cells reference exists (`silent_cells.tex` is generated but never `\input`).

**Verification after the edits:** abstract 246 → **199 words** (LaTeX-stripped count; the
math tokens make this an over-count, so the Word figure is ~196, under the SR 200 ceiling).
`pdflatex ×3` on `main.tex`: 0 errors, 0 undefined, 19 pp. `response_to_reviewers.pdf`
rebuilt, 3 pp. `build_revision.sh`: **ACID PASS** (0/0/19 pp from a clean extract with
`TEXMFHOME` hidden). `pytest`: **27 passed**. Hub `audit_gate.py`: **mechanical gates PASS**
(23 claim anchors, 39 columns, 6 controls, R6 all-resolve).

> **AUTHOR: the numbers in items 1–4 changed after the 08-11 verdict was drafted.** If you
> read the manuscript or the response letter before 08-12, re-read §4.7, §4.9 and the letter's
> opening paragraph before signing AUD-5..10 — the corrected values are what will ship.

**Tier A — corrections (do before upload; A1/A2 are real defects found by self-check):**

- **A1. Abstract 240 words → ≤200 (SR limit; my rewrite overgrew it).** Drafted replacement
  (~198w, count at execution): keep sentences 1–2 verbatim; compress the design sentence to
  "…and apply it to twelve public clinical datasets ($n=155$–$101{,}763$), three rankers, three
  learners, and budgets from 100% to 25% of features plus matched exact-$k$ budgets
  ($k\in\{1,2,4,8\}$), with paired, multiplicity-corrected, bootstrapped comparisons."; keep the
  counts sentence; compress the k/flip material to "The harm tracked the absolute retained
  count: at $k=1$ every dataset was materially harmed, and reduction flipped 21% of biopsy
  decisions on the mammographic data at threshold 0.10."; compress recal to "Post-hoc
  recalibration repaired only the random forest's calibration error, recovering none of the
  selective-reliability or net-benefit loss."; closing sentence unchanged.
- **A2. main.tex:953 STALE Data-availability sentence** ("The Diabetes-130 cohort is
  deterministically stratified-subsampled to n=6{,}000 … for tractability") → replace with:
  "The Diabetes-130 cohort is analysed in full ($n=101{,}763$ eligible encounters); the
  $n=6{,}000$ deterministic subsample of the originally submitted version survives only as the
  registered robustness arm (Section~\ref{sec:fullcohort})."
- **A3. Full consistency/denoise sweep** of the 19pp against the results JSONs (the ns-fraud
  3-pass precedent; today's rewrite touched every section). Known suspects to harmonize:
  §4.3 "The robust datasets are those with many candidate features…" still reads like the
  retired claim (soften to "the datasets that appear robust under fractional budgets…");
  check §4.8/§4.9 tense + cross-refs; check every \result{} against meta_k/safe_budget/
  worked_example/v1_v2_diff JSONs; check no leftover "silent cells table" reference; check
  Fig/Table numbering after float additions.
- **A4. Algorithm 1 + Fig 1 (TikZ) describe only fractional budgets** — add to Algorithm 1's
  \Require line "budgets $\mathcal{F}$ (fractional and exact-$k$ levels)" and one caption
  clause in Fig 1; no structural change.
- **A5. Untrack LaTeX build artifacts** (paper/*.aux, *.log, *.out, response_to_reviewers.aux)
  + gitignore them — the public flip should not ship build litter.
- **A6. AFTER A1–A5 (compute):** pdflatex ×3 + rebuild certify-feature-reduction_SR_revision.zip +
  acid test + pytest; verify abstract ≤200 by count; commit/push.

## ✅ RESOLVED 2026-08-12 — option (a) taken: reported, and the claim re-based

The author chose to report it. §4.7, Fig.~\ref{fig:stability}'s caption, the Discussion, the
Conclusion and the response letter now rest the "not selection noise" claim on a **dissociation**
instead of a correlation, and disclose the trend as measured:

- **Haberman** — 2nd most stable of twelve (Jaccard 0.93), **3rd most harmed** (+0.060).
- **SPECTF** — among the least stable (0.51), **least harmed** (+0.002).
- Plus the exact-$k$ arm, which makes the point without reference to stability at all: at $k=1$
  every dataset is materially harmed, including those with near-deterministic selections.
- The correlational test is reported in both directions: null across datasets (+0.14, p=0.66,
  n=12), null pooled at (dataset, ranker) level (−0.047, n=36), and a weak within-dataset trend
  (−0.29, block-permutation p=0.19) **whose sign is the one a noise mechanism predicts** — stated
  as non-significant and confounded with ranker quality, and explicitly not relied upon.

`ranking_stability.py` emits the block-permutation test (20,000 permutations, seeded from
`RANDOM_SEED`, 12 blocks) so the p-value is anchored, not hand-computed. The Discussion and
Conclusion previously asserted the null flatly; both now state the evidence instead ("datasets
whose selections barely move are harmed anyway").

Paper is 20 pp (was 19: the retained-$k$ table plus this expansion). ACID PASS 0/0/20, pytest 27,
gates PASS.

### The original decision note, for the record

## OPEN DECISION — the stability null at the (dataset, ranker) level (2026-08-12)

§4.7 says the harm "is \emph{not} explained by instability of the selection itself", resting on
ρ=+0.14, p=0.66 over **twelve** points (mean Jaccard per dataset vs per-dataset harm). Each
ranker has its own stability *and* its own harm, so the natural unit is the (dataset, ranker)
pair — 36 points. `ranking_stability.py` now emits both. The finer test does **not** support the
sentence as written:

| test | ρ | p |
|---|---|---|
| per-dataset (n=12, what the paper reports) | +0.14 | 0.66 |
| per (dataset, ranker), pooled (n=36) | −0.047 | 0.79 |
| per (dataset, ranker), **within-dataset** (n=36) | **−0.292** | 0.19 † |

† block-permutation over the 12 independent blocks, two-sided; one-sided (the noise-hypothesis
direction) 0.096. The parametric p was 0.084 and is anticonservative — 36 rows, 12 blocks.

**Negative is the direction the selection-noise hypothesis predicts** (less stable → more harm).
So this is a weak, non-significant trend *toward* the mechanism §4.7 says is not operating. It is
also confounded: within a dataset, a better ranker is plausibly both more stable and less harmful,
so the association need not mean instability *causes* harm.

The claim survives on better evidence than the correlation ever was — but that evidence has to be
stated, because it is not the correlation:

- The two most-harmed datasets are among the **most stable**. Mammographic mass: Jaccard 0.83,
  the largest AURC penalty (+0.070). Haberman: Jaccard 0.93, third-largest (+0.060). A noise
  mechanism cannot produce that.
- The exact-$k$ arm is decisive and stability-independent: at $k=1$ **every** dataset is
  materially harmed, including the ones whose selections are essentially deterministic.

**Options for the author.** (a) *Report it* — replace the correlation-based sentence with the
two bullets above plus one honest clause conceding the within-dataset trend and its p-value.
Costs a softened sentence; buys a claim a referee cannot dismantle, and pre-empts the analysis
any reader can run in ten minutes once the repo is public. **This is my recommendation.**
(b) *Leave §4.7 as written* — the n=12 null is what was pre-planned, and the n=36 layer is a
post-hoc analysis; but it is now in the repo, and a public repo containing an unreported result
that cuts against a Results sentence is precisely the exposure the 2026-07-17 lesson is about.

**The manuscript is unchanged pending this decision.** Nothing else in the package depends on it.

**Tier B — discretionary (author decision, not blocking upload):**

- **B1. Zenodo deposit** (program convention: one deposit per paper, citable concept DOI in
  Code availability, Restricted→Open; ~100 MB bundle; AUTHOR mints — public+permanent).
  Recommended: yes, adds a permanence layer the public GitHub flip alone lacks.
- **B2. Regenerate the graphical abstract** to the retained-count headline (matplotlib run;
  SR does not require it; currently declared not_run in MANIFEST).
- **B3. Title: recommend UNCHANGED** — it already states the strengthened finding; mid-review
  title changes cost recognition continuity.
