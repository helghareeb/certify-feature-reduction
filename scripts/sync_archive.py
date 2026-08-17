"""Mirror the complete study onto an external drive, and keep it current.

Assembled by hand the first time, which is fine once. It is not fine repeatedly: this will be
re-run after every change from here to submission, and a hand-assembled copy drifts silently
from the thing it is supposed to preserve.

What it copies: both repositories in full (including `.git`, so history and provenance
survive), every intermediate artifact that is deliberately not committed, and the delivery
channel. It skips `.venv` -- half a gigabyte of platform-specific binaries that
`pip install -r requirements.lock.txt` regenerates exactly.

Incremental by default: a file is copied only when its size or mtime differs, so an update
after a small change takes seconds rather than minutes.

    python scripts/sync_archive.py                  # update I:\\certify-feature-reduction-complete
    python scripts/sync_archive.py --dest F:\\...    # somewhere else
    python scripts/sync_archive.py --verify         # re-hash the destination, change nothing

**Verification is the point, not the copy.** The usual destination is a drive that has
reported bad-sector noise, and a silently corrupt copy is the failure that matters -- so the
hashes are computed by reading the files back *from the destination*, never from the source.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import time
from pathlib import Path

DEFAULT_DEST = Path(r"I:\certify-feature-reduction-complete")

SOURCES = [
    (Path(r"E:\Github\certify-feature-reduction"), "01_private_repo_certify-feature-reduction"),
    (Path(r"E:\Github\certify-feature-reduction"), "02_public_compendium_certify-feature-reduction"),
    (Path(r"H:\ملفاتي\nadia-pc\04_additional_papers\TASK-014-nsclin-enrichment"), "03_delivery_channel_TASK-014"),
]
SKIP_DIRS = {".venv", "__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
MANIFEST = "BUNDLE.sha256"


def needs_copy(s: Path, d: Path) -> bool:
    if not d.exists():
        return True
    ss, ds = s.stat(), d.stat()
    return ss.st_size != ds.st_size or int(ss.st_mtime) != int(ds.st_mtime)


def sync_one(src: Path, dst: Path) -> tuple[int, int, int]:
    copied = skipped = failed = 0
    for root, dirs, names in os.walk(src):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        out = dst / Path(root).relative_to(src)
        out.mkdir(parents=True, exist_ok=True)
        for n in names:
            s, d = Path(root) / n, out / n
            if not needs_copy(s, d):
                skipped += 1
                continue
            try:
                shutil.copy2(s, d)
                copied += 1
            except PermissionError:
                # git pack/idx files are written read-only, so copy2 cannot overwrite them.
                # Clearing the attribute and retrying is the whole fix; without it the .git
                # history on the archive silently stops updating while everything else does.
                try:
                    os.chmod(d, 0o666)
                    shutil.copy2(s, d)
                    copied += 1
                except OSError as e:
                    failed += 1
                    print(f"    !! {s.name}: {e}")
            except OSError as e:
                failed += 1
                print(f"    !! {s.name}: {e}")
    return copied, skipped, failed


def hash_dest(dest: Path) -> list[str]:
    lines, bad = [], 0
    for root, dirs, names in os.walk(dest):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for n in sorted(names):
            if n == MANIFEST:
                continue
            p = Path(root) / n
            try:
                lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  "
                             f"{p.relative_to(dest).as_posix()}")
            except OSError as e:
                bad += 1
                print(f"    !! unreadable ON THE DESTINATION: {p.relative_to(dest)} ({e})")
    if bad:
        print(f"  {bad} file(s) could not be read back -- treat this copy as suspect")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=str(DEFAULT_DEST))
    ap.add_argument("--verify", action="store_true", help="re-hash the destination; copy nothing")
    a = ap.parse_args()
    dest = Path(a.dest)

    if not dest.drive or not Path(dest.drive + "\\").exists():
        print(f"destination drive {dest.drive} is not connected")
        return 1

    if a.verify:
        man = dest / MANIFEST
        if not man.exists():
            print(f"no {MANIFEST} at {dest}")
            return 1
        want = {}
        for line in man.read_text(encoding="utf-8").splitlines():
            if line.strip():
                h, _, rel = line.partition("  ")
                want[rel] = h
        have = {ln.split("  ", 1)[1]: ln.split("  ", 1)[0] for ln in hash_dest(dest)}
        bad = sorted(r for r in set(want) & set(have) if want[r] != have[r])
        missing = sorted(set(want) - set(have))
        extra = sorted(set(have) - set(want))
        print(f"\n{len(want)} listed | {len(bad)} corrupt | {len(missing)} missing | {len(extra)} new")
        for r in (bad + missing)[:15]:
            print("   ", r)
        return 1 if (bad or missing) else 0

    dest.mkdir(parents=True, exist_ok=True)
    print(f"destination: {dest}\n")
    tc = ts = tf = 0
    for src, name in SOURCES:
        if not src.exists():
            print(f"  SKIP  {name}  (not reachable)")
            continue
        t0 = time.time()
        c, s, f = sync_one(src, dest / name)
        tc, ts, tf = tc + c, ts + s, tf + f
        print(f"  {name:<52} {c:>5} copied  {s:>5} unchanged  {f:>3} failed  {time.time()-t0:>5.0f}s")
    print(f"\n  {'TOTAL':<52} {tc:>5} copied  {ts:>5} unchanged  {tf:>3} failed")

    print("\nre-hashing the destination (reading back from the drive, not the source)...")
    lines = hash_dest(dest)
    (dest / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"  {MANIFEST} covers {len(lines)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
