"""Sync the private working repo into the public compendium.

Two corrections are baked in here, both of them mistakes made on 2026-08-16 and both worth
stating so they are not repeated:

1. **Hand-copying is not a process.** Three files were copied across by hand and silently
   reintroduced strings that had already been removed once. A normalisation that depends on
   remembering it is one that will eventually not be done.

2. **Nothing under `results/` is rewritten, and nothing is dropped.** The first version of
   this sync edited text inside delivered result folders and broke fifteen author-signed
   manifests; the reaction was to drop those files from the public tree entirely, which
   removed pre-ruled outcomes and negative findings from the scientific record to solve a
   problem that turned out not to exist. **Completeness wins.** Result folders are copied
   byte-for-byte, their manifests keep verifying, and only the FOLDER NAMES change --
   manifests list bare filenames, so renaming a folder is safe.

Text normalisation applies to the manuscript and repo-level prose only: the old repository
slug becomes the new one, and paths are updated to the renamed folders.

    python scripts/sync_public.py --check     # report, change nothing; non-zero if work is due
    python scripts/sync_public.py             # normalise in place
"""
from __future__ import annotations

import argparse
import os
import re
import sys

SRC = r"E:\Github\certify-feature-reduction"
DST = r"E:\Github\certify-feature-reduction"

RENAME = {
    "enrichments/00_environment_gate": "enrichments/00_environment_gate",
    "enrichments/01_ece_bin_sensitivity": "enrichments/01_ece_bin_sensitivity",
    "enrichments/02_high_dimensional_arm": "enrichments/02_high_dimensional_arm",
    "enrichments/03_recalibrators_beta_temperature": "enrichments/03_recalibrators_beta_temperature",
    "enrichments/04_ensemble_disagreement_confidence": "enrichments/04_ensemble_disagreement_confidence",
    "enrichments/05_gradient_boosting_bin_sweep": "enrichments/05_gradient_boosting_bin_sweep",
    "enrichments/06_distance_to_support_confidence": "enrichments/06_distance_to_support_confidence",
    "enrichments/07_sample_size_vs_width": "enrichments/07_sample_size_vs_width",
    "enrichments/08_cross_dataset_correlates": "enrichments/08_cross_dataset_correlates",
    "enrichments/09_signal_concentration_16ds": "enrichments/09_signal_concentration_16ds",
    "enrichments/09_signal_concentration": "enrichments/09_signal_concentration",
    "enrichments/10_independence_vs_sample_size": "enrichments/10_independence_vs_sample_size",
    "enrichments/10b_cross_axis_coherence": "enrichments/10b_cross_axis_coherence",
    "enrichments/11_recalibrator_flexibility_ladder": "enrichments/11_recalibrator_flexibility_ladder",
    "enrichments/12_probe_injection_dose_response": "enrichments/12_probe_injection_dose_response",
    "enrichments/12b_kept_set_composition": "enrichments/12b_kept_set_composition",
    "enrichments/13_safe_budget_diagnostic": "enrichments/13_safe_budget_diagnostic",
    "enrichments/14_surviving_penalty_localisation": "enrichments/14_surviving_penalty_localisation",
    "enrichments/15_matched_absolute_budget": "enrichments/15_matched_absolute_budget",
}
ORDER = sorted(RENAME, key=len, reverse=True)   # tier9_16ds before tier9

SLUG = re.compile(r"certify-feature-reduction")
TEXT = {".md", ".toml", ".tex", ".txt", ".py", ".cff", ".yml", ".yaml"}
NEVER = {"AGENT_COORDINATION.md", "SESSION_COORDINATION.md", "AGENTS.md",
         "PROVENANCE_NOTE.md", "REVISION_NOTES.md", ".venv", ".pytest_cache",
         "__pycache__", ".git"}

# A public repo must never name the private rules repository or its tooling. These are
# internal machinery: a reader cannot reach them, and advertising them helps no one.
HUB = [
    ("an internal pre-submission audit gate", "an internal pre-submission audit gate"),
    ("the pre-submission audit gate", "the pre-submission audit gate"),
    ("The pre-submission audit gate", "The pre-submission audit gate"),
    ("the pre-submission audit gate", "the pre-submission audit gate"),
    ("the audit gate", "the audit gate"),
    ("the audit gate", "the audit gate"),
    ("internal rules", "internal rules"),
    ("the internal rules repository", "the internal rules repository"),
]


def normalise(text: str) -> str:
    for k in ORDER:
        text = text.replace(k, RENAME[k])
    for a, b in HUB:
        text = text.replace(a, b)
    return SLUG.sub("certify-feature-reduction", text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only; exit non-zero if work is due")
    a = ap.parse_args()

    due, fixed = [], 0
    for root, dirs, files in os.walk(DST):
        dirs[:] = [d for d in dirs if d not in NEVER]
        rel_root = os.path.relpath(root, DST)
        # results/ is the scientific record: byte-exact, manifests must keep verifying
        if rel_root.split(os.sep)[0] == "results":
            for fn in files:
                if SLUG.search(fn):
                    due.append(("PATH", os.path.join(rel_root, fn)))
            continue
        for fn in files:
            p = os.path.join(root, fn)
            r = os.path.relpath(p, DST)
            if SLUG.search(r):
                due.append(("PATH", r))
                continue
            if os.path.splitext(fn)[1].lower() not in TEXT:
                continue
            try:
                t = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            n = normalise(t)
            if n != t:
                due.append(("CONTENT", r))
                if not a.check:
                    open(p, "w", encoding="utf-8", newline="").write(n)
                    fixed += 1

    verb = "would be normalised" if a.check else f"normalised ({fixed} written)"
    print(f"{len(due)} file(s) {verb}")
    for k, r in due[:20]:
        print(f"  {k}  {r}")
    return 1 if (a.check and due) else 0


if __name__ == "__main__":
    sys.exit(main())
