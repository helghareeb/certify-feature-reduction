# Tier 9 — 16-dataset addendum (supersedes the 14-dataset delivery for coverage)

**Received from the second compute node 2026-08-15, in response to `the Tier 9 glioma request.md`.**

## Why this folder exists separately

The original 14-dataset delivery carries a `MANIFEST.sha256` that its author signed and that
verifies 4/4 on this box. This addendum arrived as a flat zip **without** a replacement manifest, so
overwriting the signed files in place would have broken that manifest — and a broken manifest is
indistinguishable from corruption to anyone auditing later. The 14-dataset delivery is therefore left
byte-intact, and the superseding computation lives here, with its provenance recorded honestly as
what it is: **a verified transport hash, not an author-signed content manifest.**

A signed `DONE.md` + `MANIFEST.sha256` for this addendum has been requested. When it arrives this
folder gets one and the note below can be replaced.

## Provenance

| | |
|---|---|
| transport | `the delivery archive` |
| declared sha256 | `d450ab7d39db7a1cf4f20b075efde5b49eda81a1f5a02b805316c74376619f23` |
| computed here | `d450ab7d39db7a1cf4f20b075efde5b49eda81a1f5a02b805316c74376619f23` — **match** |
| contents | `tier9_concentration.csv` (8,789 B), `tier9_correlation.json` (584 B) |

## What changed

Coverage only. The 14-dataset version held the twelve clinical datasets plus `arrhythmia`,
`prostate_ge` and `arcene` — 14 in total, because `diabetes130` was also absent. This version holds
**16**: the same set plus **`gli85`** and **`diabetes130`**.

`gli85` is the one that mattered. The manuscript's high-dimensional section had been ordering **four**
datasets by concentration while the statistic existed for only **three** of them.

## What it settled

The missing measurement did **not** rescue the ordering claim. With all four datasets present:

| statistic | reproduces the harm ordering? |
|---|---|
| raw top-$k$ share, $L_1$-logistic | 4 / 4 budgets ✅ |
| raw top-$k$ share, mutual information and RF importance | 0 / 8 ❌ (arrhythmia ranks first — a width artefact) |
| Gini (scale-free) | 0 / 3 ❌ (`gli85` ranks first; arcene above arrhythmia) |
| **lift over uniform**, $\text{top-}k\text{ share}\big/(k/p)$ — the principled width correction | **0 / 21** ❌ |

The lift statistic is the natural correction for the incomparability that caused the failure in the
first place, and it was computed across every ranker and every budget before its answer was known. It
refutes the ordering decisively and consistently places `arrhythmia` **last** in concentration though
it is the second-most harmed.

What survives every statistic, every ranker and every budget — including the corrected one — is the
**prostate-vs-arcene contrast**: prostate is the more concentrated and the less harmed in all cases.
The manuscript claims that and no more.

Reported rather than discarded: this is a negative result about our own proposed explanation, and it
is in the paper.
