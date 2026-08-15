# AUDIT REPORT — `certify-feature-reduction`, pre-resubmission audit

**Paper:** *Aggressive feature reduction degrades the selective reliability and clinical net benefit
of clinical risk models* · Scientific Reports submission `2650209c-ff1e-4df4-aeb0-75ef3b35e564`
(revision).
**Audited:** 2026-08-15, against `AUDIT_RULES.md` (`AUD-0`–`AUD-12`) in the author's rules hub.
**Method:** the manuscript read against its own released code and results, not against itself. Every
number was recomputed here from the raw CSVs before being accepted, including numbers delivered with
a summary that already stated them.

> **Status: mechanical gates PASS. The human gates `AUD-5`–`AUD-12` require the author's signature;
> `AUD-0` blocks resubmission until that signature exists.** Two experiments are still running
> (`P1 v2`, `P6`); this report is current as of the manuscript at commit `9893b94` and must be
> re-run before the package is uploaded.

---

## 1. Mechanical gates

| gate | result | note |
|---|---|---|
| `AUD-1` Ran | **PASS** | 12 scripts ledgered or declared; the `[not_run]` entry for the all-rankers wrapper was retired in the same commit as the section that consumes its output, so it never outlived its truth |
| `AUD-2` Reported | **PASS** | 105 result columns; every one cited or declared in `MANIFEST.toml` with a reason. Began at 24 undeclared — see §3.1, one of them contradicted the paper |
| `AUD-2` Macros | **PASS** | all defined macros referenced |
| `AUD-3` Implemented | **PASS** | 23 anchors resolve mechanically, and **all 23 have been read against their code** — §3.7. One was overstated and is reworded; one claim about *timing* was verified against git ancestry instead |
| `AUD-4` Falsifiable | **PASS** | 6 controls vary; no zero-width CI |
| `R6` calibration | **PASS** | every stamped result resolves to one of 10 shipped calibrations — after both a missing-file fix and a **gate bug**, §3.2 |

## 2. Human gates — findings

| gate | verdict | basis |
|---|---|---|
| `AUD-5` Title | **PASS, with one note** | Every load-bearing word is measured: aggressive reduction is the intervention, and both named axes are materially worse (94 and 80 of 108 cells). No method is named that the code does not implement. **Note:** "selective reliability" is now qualified in the text — two-thirds of the measured AURC harm is a property of the probability scale (§3.4). A title change was considered and **declined**: the claim as written remains true under the standard confidence definition, the surviving third is decisive, and re-titling a manuscript mid-review costs the reviewers their frame of reference for no gain in accuracy |
| `AUD-6` Abstract | **PASS after edit** | Every claim traces to a result. The two-thirds qualification was added; the abstract sat at 199 words against a 200 ceiling, so the edit was made **net-neutral** by compression rather than by exceeding the limit. Now exactly 200 |
| `AUD-7` Experiments | **PASS** | The unit of analysis is correct throughout: **108 is never used as an inferential $n$** — it is a count of cells, not of observations. Cross-dataset correlations use $n=12$; the finer (dataset, ranker) correlation uses a **block permutation over the twelve independent datasets**; the meta-analysis is explicitly labelled exploratory. Controls are pre-registered with pre-ruled outcomes, including the two that returned against us |
| `AUD-8` Discussion | **PASS after fix** | One causal claim was not earned and has been removed — §3.3 |
| `AUD-9` Conclusion | **PASS** | Introduces no claim absent from Results; the single "we did not pursue it further" refers to ensemble disagreement and remains true; "future work should include prospective and temporally split validation" is genuinely not in the paper |
| `AUD-10` References | **PASS after fix** | 0 orphans, 0 cited-but-unlisted against the real (inline) bibliography. Two fixes — §3.5 |
| `AUD-11` No advocacy | **PASS after fixes** | Three violations found **in our own paper** — §3.1, §3.3, §3.4 |
| `AUD-12` Fingerprint | **PASS** | Every result entered the manuscript only after its `sha256` manifest verified here. Three near-misses caught — §4 |

---

## 3. Changes made, by issue type

### 3.1 Uncited result contradicting the paper — `AUD-2`, `AUD-11`

| | |
|---|---|
| **Where** | `main.tex` §High-dimensional arm; `results/enrichments/09_signal_concentration_16ds/tier9_concentration.csv` column `gini` |
| **Before** | "Ranked from least to most harmed---prostate, glioma, arrhythmia, arcene---they follow the concentration of predictive signal measured from the ranking scores themselves." |
| **Issue** | The ordering claim covered **four** datasets using a statistic measured for **three** — `gli85` was absent from the concentration run entirely. Tested across three rankers × three statistics the ordering held **2 of 9**. `gini`, a committed column the paper never cited, ranks arcene *above* arrhythmia under **all three** rankers while arcene is the more harmed. Applying the principled correction for the width incomparability (top-$k$ share ÷ $k/p$, the share a uniform ranker achieves) across **21** ranker × budget combinations reproduced the ordering **0 times**, and placed arrhythmia *last* in concentration though it is second-most harmed |
| **After** | The ordering claim is withdrawn. The section now reports only the prostate-vs-arcene contrast (robust 9/9), states the arrhythmia width incomparability and the Gini disagreement explicitly, reconciles the two statistics, and reports the 0-of-21 result as a negative finding about the paper's own explanation |
| **Provenance** | `gini` is declared in `MANIFEST.toml` with the contradiction and its reconciliation recorded, not quietly marked out of scope |

### 3.2 Calibration provenance — `R6`, and a bug in the gate itself

| | |
|---|---|
| **Where** | `config/`; `scripts/audit_gate.py` in the rules hub |
| **Before** | Six `calibration_sha256` stamps in the delivered results resolved to no file in the repository. Under `R6` that reads as drift and blocks submission |
| **Issue (two layers)** | (a) The configurations that produced the arrhythmia subsampling, high-dimensional and four-recalibrator runs lived only on the collaborator's machine and had never been shipped. (b) **More seriously, the gate was wrong**: it hashed each config file's *bytes*, while the stamp is `sha256` over the config's **canonical JSON serialisation** (`src/nsclinfs/hashing.py`). The two coincide only when the file was written by that serialiser — true of all four configs authored in this repository, which is why hashing bytes had never failed and had never been tested against a config written anywhere else |
| **After** | Six configs committed byte-exact (they were correct; the gate was not), with a `CALIB_MAP.md` recording each stamp against its file. The gate now accepts either hash; this cannot create a false pass, because a stamp must still resolve to a committed, tracked file |
| **Scope** | The gate fix is portfolio-wide. The same failure class is already documented in that function's own comment for another paper, where the recommended action for an unresolved stamp is **withdrawal** |

### 3.3 Causal claim not earned, and stale — `AUD-8`, `AUD-11`

| | |
|---|---|
| **Where** | `main.tex` §Discussion, "Practical guidance" |
| **Before** | "Because the harm is heterogeneous but **predictable**, the decision should be made per dataset and per learner---guided by the **feature-count / intrinsic-dimension screen above**---rather than by a single global rule." |
| **Issue** | Direct internal contradiction. Results state that **no** proxy — not dataset width, not any other property measured — certifies a budget in advance. The named screen is precisely what this revision withdrew in response to Reviewer 1. The sentence survived the rewrite and pointed readers at a criterion the same manuscript retracts two sections earlier |
| **After** | "Because the harm is heterogeneous and no dataset property we measured certifies a budget in advance, the decision must be made per dataset and per learner by *running* the audit, not by consulting a proxy for it. The retained count locates where the risk concentrates … but that identifies a high-risk regime rather than certifying a safe one." |
| **Second location** | **The same withdrawn claim was also in the cover letter to the editor** — "a cross-dataset meta-analysis shows the harm is predictable in advance from the feature count and intrinsic dimensionality." Removed; the letter was rewritten (§5) |

### 3.4 A qualifying result buried while the supporting one led — `AUD-11`

| | |
|---|---|
| **Where** | `main.tex` §Discussion and Abstract |
| **Before** | The Discussion led with "degraded selective reliability (AURC, worse in 94 of 108 cells)" and called the deployment-relevant harms "the most robust signal". The measurement showing that **two-thirds of that harm is a property of the probability scale** appeared only in Limitations |
| **Issue** | The supporting number was prominent and the qualifying number was not. This is the shape `AUD-11` forbids, in our own paper |
| **After** | The qualification sits beside the headline in the Discussion, stated as a measurement (+0.0334 → +0.0116 under a feature-space confidence), and in the Abstract. The revised claim is *stronger*, because the surviving third is what makes the result evidence of a genuine loss of error-ordering rather than a restatement of the calibration finding |
| **Related** | Net-benefit recovery was described as "flat ≈ 0"; it is strictly monotone in recalibrator flexibility ($\rho=+1.00$) and merely **small** (0.9 % of baseline against 27.8 % for ECE). Re-described by magnitude, not direction |

### 3.5 References — `AUD-10`

| | |
|---|---|
| **Where** | `refs.bib`; `main.tex` Methods |
| **Issue A** | The bibliography is **inline** (`\thebibliography`), so `refs.bib` is not the build input and can rot with no warning. It had: `strack2014impact`, the Diabetes-130 dataset citation the manuscript cites twice, was missing. Anyone regenerating the bibliography from it would have silently dropped a reference |
| **Issue B** | Four foundations of quantities the paper measures — ECE, the Brier score, AURC, and Platt/isotonic recalibration — were defined in Methods with their sources cited only in the Introduction |
| **After** | `refs.bib` resynchronised (23 keys both sides); citations added at the definitions. The seven keys that remain front-matter-only are motivation (feature-selection reviews, fairness, calibration-in-medicine guidance), which is where they belong |

### 3.6 Regeneration contract — `R1`

Two measured numbers were hardcoded in prose while the same quantities were `\result{}`-wrapped
elsewhere: the retained-count and width correlations in the Discussion, and the $-0.90$ flexibility
correlation in the ladder footnote (the latter introduced by this audit's own additions). A number
that regenerates in one place and is typed in another is exactly how the two drift apart. Both fixed;
a repository-wide scan now shows no measured decimal outside `\result{}` — the remaining hits are
figure widths and the chosen clinical threshold.

### 3.7 `AUD-3` — claims read against their code, not merely located

The gate proves a claim's anchor line exists; only a reader proves it *acts*. Seven load-bearing
claims were read against their implementation, chosen because each is one whose code could plausibly
exist and be discarded.

| claim | verdict |
|---|---|
| AURC uses confidence $\lvert p-0.5
vert$ | **Acts.** Exactly one call site: `aurc(y, p_oof, np.abs(p_oof - 0.5))`. The function takes confidence as a parameter, which is the shape that lets a claim drift from its call site; it has not |
| Leakage firewall: imputation, ranking, standardisation and fitting inside the training fold | **Acts.** All four are training-fold-only in `run.py`: the imputation median from `X.iloc[tr]`, the ranking from `Xtr_i`, the standardisation $\mu,\sigma$ from `Xtr_i[feats]` applied to both sides, and the fit on train predicting test |
| Paired design: folds and rankings computed once and shared across budgets | **Acts.** Folds and per-fold rankings are built before the budget loop, so every level is paired with every other and with the full-feature reference |
| Holm families computed *within* `budget_type` | **Acts.** The family key is literally `row["budget_type"]`, and Holm is applied per family — so the exact-$k$ arm cannot move the fractional-family corrections |
| Selective ECE on the 80\,\% most-confident subset | **Acts.** `conf = np.abs(p - 0.5)` at the subsetting site |
| Materiality = Wilcoxon + Holm **and** a bootstrap CI excluding zero | **Acts.** Both are computed per row and both gate the verdict |
| R6 enforced at every read/merge path | 🔴 **Overstated as written, and one real gap found.** `assert_single_hash` is called by nine consumers and has a dedicated test whose docstring records that it spent v1 as dead code. But `meta_analysis_k.py` — which produces `meta_k.json` and the retained-count table, i.e. the $
ho=-0.78$ the Discussion leans on — used a **hand-rolled** copy of the guard that tested only `len(hashes) > 1`. A summary carrying **no** calibration stamp at all passed it silently, and an absent stamp is exactly as bad as a conflicting one |

**Fixed:** `meta_analysis_k.py` now calls the shared `assert_single_hash`. Re-run under the pinned
environment: `meta_k.json` and `meta_k_table.tex` are **byte-identical**, so the change is
behaviour-preserving on valid input and strictly stricter on invalid input. Test suite 27/27.

**Claim reworded** rather than left absolute. Two exclusions are deliberate and are now stated in
`MANIFEST.toml`: `launch_grid.py` counts rows for resume logic and never analyses them, and
`v1_v2_diff.py` exists precisely to compare the archived v1 aggregates against the rebuild *across*
configurations, so the guard would defeat its purpose — its output is quoted only in the response
letter, never in the manuscript.

**The remaining sixteen anchors have since been read as well — all 23 are now audited.** They act as
claimed. The ones worth naming, because each is a place a claim could have drifted from its code:

| claim | what the code actually does |
|---|---|
| Budget rule with the $\geq1$ floor and round-half-to-even | `max(1, int(round(frac * n_features)))`. Python's `round` is banker's rounding, so $p=5$ at $0.5$ retains 2, not 3. The docstring records both properties as **deliberately preserved, not fixed** |
| Exact-$k$ budgets share the fractional arm's repetitions and folds, with equal $k$ deduped | The level loop runs over `sorted({k for *_, k in levels})` — a set, so a $k$-level equal to a frac-derived $k$ is computed once and is bitwise the same model |
| Net benefit $\mathrm{NB}(t)=\mathrm{TP}/n - (\mathrm{FP}/n)\,t/(1-t)$, averaged over $t\in[0.05,0.5]$ | Implemented exactly, averaged over 19 evenly spaced thresholds in that range |
| Split-conformal at 90 % nominal, set size as the reported axis | $lpha=0.1$; nonconformity $1-p_{	ext{label}}$; threshold the $(1-lpha)$ empirical quantile with `method="higher"` (the conservative choice); `conformal_efficiency` returns the mean set size |
| Subgroup gaps guarded at $\geq10$ samples **and** both classes present | `if m.sum() < 10 or len(np.unique(y[m])) < 2: continue`, and `_gap` returns `NaN` below two usable groups — which is why three datasets are reported as undefined rather than as zero |
| Leakage-safe recalibration by inner 3-fold within the training fold | `CalibratedClassifierCV(base, method=calibrate, cv=3).fit(Xtr, ytr)`; the outer held-out fold enters only through `predict_proba` |
| The full cohort is config-driven, `n_target: null` meaning all encounters | `if n_target is not None and len(X) > n_target:` — the subsample is *skipped* when null, and the `stratify` branch selects outcome-only or joint outcome-race strata |
| Selection stability: mean pairwise Jaccard over the per-fold rankings | Mean over `combinations(sets, 2)` of top-$k$ sets, from rankings built with training-fold-only imputation |
| Strict certificate: no materially-worse cell on **any** axis | Safety at a budget requires `material_worse.sum() == 0` across all cells and axes at that $k$ |
| Subsample agreement on CI overlap, sign and verdict | All three computed (`ci_overlap`, `sign_agree`, `verdict_agree`); the two configurations are hash-checked **separately** rather than merged, which is the correct treatment of a deliberate cross-configuration comparison |
| Cross-dataset screen with leave-one-dataset-out and a seeded 5000-resample bootstrap | Both present: a per-dataset `lodo` map and a 5000-iteration percentile CI |
| Dataset descriptors computed from the same loaders under the same `dataset_params` as the grid | `params` is read from the calibration config and passed to the same `dataload.load`, so a descriptor cannot be computed on a different subsample from the one the grid ran |

### The one claim verified against history rather than against code

*"The worked example's cell and threshold were fixed a priori"* is a claim about **when**, which no
amount of reading the file can settle. Checked against git ancestry instead:

| | |
|---|---|
| `5784dfd` 2026-08-11 **01:11** | `config/analysis.json` committed — cell and threshold $t=0.10$ fixed |
| `e235a41` 2026-08-11 **05:10** | `worked_example.py` committed — the first code capable of computing a flip count |
| `1e3b1e8` 2026-08-11 **20:27** | the flip numbers enter the manuscript |

Strict ancestry, verified with `git merge-base --is-ancestor` in both links. The threshold was fixed
**four hours before any code existed that could compute a flip rate**, and nineteen hours before a
flip number reached the paper. Once the repository is public a reviewer can run the same two commands.


### 3.8 The enrichment code, and a leak that was visible in exactly one place

The Arm B finding prompted the obvious question — does anything else carry the same pattern? — and the
answer was that we could not tell, because **one of eighteen enrichments had shipped its code.** The
rest existed in this repository as numbers. That is now fixed: all twenty-one scripts and the frozen
library copy they ran against are committed under `experiments/enrichments/`, and `AUD-1 (Produced)`
was added to the gate so the gap cannot reopen silently.

Every script was then read against three questions:

1. Does any **label-informed** choice happen outside the cross-validation?
2. Does any statistic computed on **all rows** enter a per-fold model?
3. Are **imputation, ranking and standardisation** fitted on the training fold only?

**Result: the leak was in P1 Arm B and nowhere else.** Two results are worth stating individually
because the manuscript leans on them hardest:

| experiment | what the code shows |
|---|---|
| **Tier 6** — the $-d$ confidence carrying "two-thirds of the harm is scale-borne" into the Abstract | **Clean.** The `BallTree` is built on `Xtr_z` — the training fold — and queried with the held-out rows; the source comment states it outright (*"held-out rows not in the tree"*). Imputation median and standardisation $\mu,\sigma$ are training-fold only |
| **Tier 9** — the concentration index | **Clean.** The ranker scores are recomputed **inside each training fold** and averaged across folds; the index never sees a held-out row. A scan flagged the scoring *function* because it has no fold context of its own, and the *call site* is inside the fold loop |

The remaining flags were false positives on inspection: an import line, a pandas rank-normalisation
helper, a constant list, and a comment.

**One asymmetry is worth recording rather than glossing.** Had Tier 9 or P3 been label-informed, it
would have made their results *optimistic* — and both are **negative**. A predictor built with label
knowledge that still fails to predict is a stronger negative, not a weaker one. They are not
label-informed, so the point is moot here; but it is the direction to check first whenever a null
result rests on a constructed predictor.

---

## 4. Deliberately **not** changed, and why

| item | decision |
|---|---|
| **The title** | Kept. Every word is earned; see `AUD-5` above. Re-titling mid-review costs the reviewers their frame of reference and buys no accuracy |
| **P1 Arm B (kept-set ladder)** | **Excluded from the manuscript, and the exclusion is declared, not silent.** Its aggressive budget was 25 % of the kept set, so $k$ rose 25 → 2500 down the ladder; the resulting U-shape confounds kept-set composition with the absolute retained count — which is *this paper's own headline effect*. A re-run holding $k$ fixed at 25 was requested and is running. Reporting it with a caveat would have been worse than omitting it |
| **P1 dose-response called a *direction*, not a measured effect** | The delivered CSVs carry one row per cell with no dispersion, though 30 reps × 3 rankers × 2 learners were run. Cleveland's $+0.054\to+0.006$ and mammographic's $+0.086\to+0.081$ cannot be distinguished as material or not from the artifact as delivered. Dispersion requested; the text will be upgraded when it lands |
| **`gini` and the other unreported concentration shares** | Declared out of scope with reasons rather than reported. The paper quotes the budgets it actually tested against; nine nested shares would add length without information |
| **The Tier 9 addendum's folder** | The 14-dataset delivery is left **byte-intact** with its author-signed manifest verifying 4/4, and the superseding 16-dataset computation sits in its own folder recording what it actually has: a verified transport hash, **not** an author-signed content manifest. Writing into the signed folder would have broken a manifest, and a broken manifest is indistinguishable from corruption to whoever audits next. A signed manifest was requested rather than fabricated |
| **The `n=6{,}000` subsample arm** | Retained as a robustness table rather than deleted, since Reviewer 1 asked what the subsample would have missed |

---

## 5. Package and letters

| item | state |
|---|---|
| Response letter | Rewritten with a second-round section, including an explicit list of the three claims withdrawn during this audit and the reason for each. 5 pp, builds clean. Salutation is "Greetings," per `COVER-letter` — never "Dear" |
| Cover letter | **Rewritten.** It was a first-submission letter, opened "Dear Editors,", and advertised the withdrawn screening claim to the editor. Now a resubmission letter with a single-author statement and no reviewer suggestions. `cover_letter.txt` is generated *from* the `.tex` by a committed script so the two cannot drift |
| `RESPONSE.md` | Second-round enrichments logged as **E10–E18**, renumbered deliberately: `E1`–`E9` are the first round and the collaborator's own notes reused `E1`–`E5` for different work, so an unqualified "E2" already meant two things |
| Submission archive | **Not yet rebuilt.** The current `paper/submission_revision/` is the 2026-08-12 build and is stale. It must be regenerated after `P1 v2` and `P6` land, and must satisfy: no manuscript PDF (the venue compiles the source), separate figure files, the response as a separate file, no stray `.bib`, and an empty-`TEXMFHOME` compile test |

---

## 6. Three near-misses worth recording

These cost nothing in the end, and each would have been invisible in the published artifact.

1. **A silent transport failure left an empty directory that looked like a delivered result.** A
   direct pull of the four-recalibrator results across the sync mount produced
   `results/enrichments/03_recalibrators_beta_temperature/` containing **nothing**, with the correct name and no error. Had the
   flat archive not arrived, that folder would have passed for a delivery. *A name is evidence of
   nothing.*
2. **Line-ending conversion was about to break the result manifests for every future clone.** Git
   warned it would rewrite `MANIFEST.sha256`; such a manifest verifies on the machine that wrote it
   and fails everywhere else, silently, until someone tries. `.gitattributes` extended to manifests,
   markdown, JSON and shipped scripts; all 12 delivered result sets re-verified afterwards (59
   manifests, 0 failures).
3. **A master archive carried a superseded copy of a result**, and the concentration audit was
   initially run against it. The per-item delivery, not the bundle's date, is authoritative.

---

## 7. Signature

`AUD-5`–`AUD-12` are human gates. This report states the auditor's findings; it is **not** a verdict.

- [ ] Author has read §3 and accepts each change
- [ ] Author has read §4 and accepts each non-change
- [ ] Author has reviewed §3.7 — all 23 `AUD-3` anchors read against their code by the auditor
- [ ] `P1 v2` and `P6` landed, verified, and written; audit re-run against the final commit
- [ ] Submission archive rebuilt and acid-tested

**Until every box is ticked, `AUD-0` blocks resubmission.**
