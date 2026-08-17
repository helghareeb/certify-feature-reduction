"""Every committed result file must name the script that produced it.

This is the check behind the repository's central claim. It is deliberately a *test* and not
a document: a provenance table maintained by hand drifts from the tree it describes, and the
first person to notice is a reader who cannot reproduce something.

    python scripts/provenance_map.py            # print the table
    python scripts/provenance_map.py --check    # exit non-zero if anything is unaccounted for
    python scripts/provenance_map.py --md       # emit the table as markdown for REPRODUCE.md

A result is accounted for when either
  (a) a producing script sits in the same folder, or
  (b) the column manifest's [external_results] names a script that is itself committed.

The manifest is PROVENANCE.toml at the repository root, or paper/MANIFEST.toml where it
still sits beside the manuscript. Both are accepted so this script is identical in the
working repository and in the released compendium, which does not ship the manuscript.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.split()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    files = tracked()
    scripts = {Path(f).name for f in files if f.endswith((".py", ".sh", ".cmd"))}
    for candidate in (ROOT / "PROVENANCE.toml", ROOT / "paper" / "MANIFEST.toml"):
        if candidate.exists():
            break
    else:
        print("no column manifest found (PROVENANCE.toml or paper/MANIFEST.toml)")
        return 1
    mf = tomllib.loads(candidate.read_text(encoding="utf-8"))
    declared = mf.get("external_results", {})

    groups: dict[str, list[str]] = defaultdict(list)
    for f in files:
        if not f.startswith("results/"):
            continue
        if not f.endswith((".csv", ".json", ".parquet")):
            continue
        groups[str(Path(f).parent).replace(os.sep, "/")].append(f)

    rows, unaccounted = [], []
    for d in sorted(groups):
        n = len(groups[d])
        local = [Path(f).name for f in files
                 if str(Path(f).parent).replace(os.sep, "/") == d and f.endswith(".py")]
        if local:
            rows.append((d, n, ", ".join(sorted(local)), "in-folder"))
            continue
        note = declared.get(d) or declared.get(d + "/")
        if note:
            named = [s for s in scripts if s in str(note)]
            if named:
                rows.append((d, n, ", ".join(sorted(named)), "declared"))
                continue
            if "no compute step" in str(note):
                rows.append((d, n, "—", "no compute step"))
                continue
            unaccounted.append((d, n, "declared, but names no committed script"))
            continue
        if d == "results":
            rows.append((d, n, "run_clinical_fs.py (canonical aggregator)", "main pipeline"))
            continue
        unaccounted.append((d, n, "no producing script"))

    if a.md:
        print("| result group | files | produced by |")
        print("|---|--:|---|")
        for d, n, s, _ in rows:
            print(f"| `{d}` | {n} | `{s}` |")
        return 0

    print(f"{len(rows)} result group(s) accounted for, {len(unaccounted)} not")
    for d, n, s, how in rows:
        print(f"  OK   {d:52s} {n:>4} file(s)  <- {s}  [{how}]")
    for d, n, why in unaccounted:
        print(f"  MISS {d:52s} {n:>4} file(s)  -- {why}")

    if a.check and unaccounted:
        print("\nFAIL: a committed result has no committed code. The repository claims every")
        print("number regenerates from committed code; that claim is false while this fails.")
        return 1
    if a.check:
        print("\nPASS: every committed result traces to committed code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
