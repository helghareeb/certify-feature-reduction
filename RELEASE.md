# 🔴 DO NOT MAKE THIS REPOSITORY PUBLIC

**This repository is private, and it stays private until the author says otherwise.**

The public release happens on **the day the manuscript is sent to the journal** — not before.

## Why this file exists

On 2026-08-15 this repository was finished, audited, and made public a few minutes early. It was
reverted immediately and nothing was lost. This note exists so the same mistake is not made twice by
someone acting in good faith.

Everything about this repo invites the flip: the README says *"public at the reviewers' request"*,
the manuscript's Code Availability section says the repository is public, the response to reviewers
promises it, and `RESPONSE.md` carries an item that reads `in-progress (flip on resubmission day)`.

**All of those are the plan. None of them is the authorisation.** Readiness is not a trigger; the
submission is.

## Why the day matters and not the readiness

Publication is irreversible in practice. Search engines index; forks persist; making it private again
does not unpublish. Before the manuscript is with the editor:

- the revision is still changing — **three claims were withdrawn in the final audit pass**, after the
  repository already looked finished;
- a public compendium can be scooped;
- the submission's own statement about *when* the code became available stops being accurate.

## The procedure

When the author confirms the manuscript has been sent:

```bash
gh repo edit helghareeb/certify-feature-reduction --visibility public
gh repo view helghareeb/certify-feature-reduction --json name,visibility
```

Then delete this file in the same commit, so it never contradicts the repository's actual state.

## The two repositories

| repo | role |
|---|---|
| `certify-feature-reduction` | the clean compendium — this one, published on submission day |
| the private provenance repo | full commit history and internal working record; **never published** |

Publishing applies to this repository only.
