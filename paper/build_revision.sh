#!/usr/bin/env bash
# Assemble the Scientific Reports REVISION package (submission 2650209c, revised manuscript).
# SR revision rules differ from first submission: NO manuscript PDF (SR compiles the source),
# figures as SEPARATE files (mandatory), and a separate response-to-reviewers file. The
# bibliography is INLINED in main.tex, so NO .bib ships (a leftover .bib beside an inlined
# bibliography is the known-confusing case). wlscirep.cls requires the jabbrv trio, which the
# SR compiler does not provide -- bundled. Regenerate all table fragments and figures FIRST
# (make_figures / meta_analysis / meta_analysis_k / safe_budget / worked_example /
# subsample_agreement / ranking_stability) so the package reflects the committed results (R1/R2).
# Run from paper/. Output: submission_revision/ + ns-clinical-fs_SR_revision.zip + acid test.
set -euo pipefail
cd "$(dirname "$0")"
OUT=submission_revision
rm -rf "$OUT"
mkdir -p "$OUT/figures"

cp main.tex "$OUT"/
cp wlscirep.cls jabbrv.sty jabbrv-ltwa-all.ldf jabbrv-ltwa-en.ldf "$OUT"/

# Table fragments and figures are DERIVED from main.tex, never listed by hand.
# 2026-08-15: the hand-written list had gone stale -- ladder_table.tex was added to the
# manuscript that morning and the package would have shipped without it. The acid test
# would have caught it, but only for someone who ran the acid test. A list that must be
# kept in sync with the manuscript is a list that will eventually disagree with it.
TABLES=$(grep -o '\\input{[^}]*}' main.tex | sed 's/.*{//;s/}//' | sort -u)
for t in $TABLES; do
  [ -f "$t.tex" ] || { echo "MISSING INPUT: $t.tex is \\input by main.tex but not present"; exit 1; }
  cp "$t.tex" "$OUT"/
done
FIGS=$(grep -o '\\includegraphics\[[^]]*\]{figures/[^}]*}' main.tex \
       | sed 's/.*figures\///;s/}//' | sort -u)
for f in $FIGS; do
  src="figures/$f"; [ -f "$src" ] || src="figures/$f.pdf"
  [ -f "$src" ] || { echo "MISSING FIGURE: $f referenced by main.tex"; exit 1; }
  cp "$src" "$OUT/figures/"
done
echo "packaged $(echo "$TABLES" | wc -w) table fragment(s), $(echo "$FIGS" | wc -w) figure(s)"

cp response_to_reviewers.pdf "$OUT"/
cp cover_letter.pdf cover_letter.txt "$OUT"/

( cd "$OUT" && rm -f ../ns-clinical-fs_SR_revision.zip && \
  python -c "import shutil; shutil.make_archive('../ns-clinical-fs_SR_revision','zip','.')" )

# Acid test: compile the package from a CLEAN extract with NO local TeX tree visible.
# (cygpath: Windows Python does not understand Git Bash /tmp paths -- translation is mandatory.)
ACID=$(mktemp -d)
ACIDW=$(cygpath -w "$ACID" 2>/dev/null || echo "$ACID")
python -c "import shutil,sys; shutil.unpack_archive('ns-clinical-fs_SR_revision.zip', r'''$ACIDW''')"
( cd "$ACID" && TEXMFHOME=/nonexistent pdflatex -interaction=nonstopmode -halt-on-error main.tex >log1 2>&1 \
  && TEXMFHOME=/nonexistent pdflatex -interaction=nonstopmode -halt-on-error main.tex >log2 2>&1 \
  && TEXMFHOME=/nonexistent pdflatex -interaction=nonstopmode -halt-on-error main.tex >log3 2>&1 )
ERR=$(grep -c "^!" "$ACID/log3" || true)
UNDEF=$(grep -ci "undefined" "$ACID/log3" || true)
PAGES=$(grep -o "Output written on main.pdf ([0-9]* pages" "$ACID/log3" | grep -o "[0-9]*" | head -1)
echo "ACID TEST: errors=$ERR undefined=$UNDEF pages=$PAGES"
[ "$ERR" = "0" ] && [ "$UNDEF" = "0" ] && echo "ACID PASS" || { echo "ACID FAIL"; exit 1; }
rm -rf "$ACID"
