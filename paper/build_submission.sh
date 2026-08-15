#!/usr/bin/env bash
# Assemble a self-contained Scientific Reports submission package (N16). The bibliography is INLINED in
# main.tex (SR does not accept .bib or re-run BibTeX), so the manuscript compiles with pdflatex alone.
# Regenerate the table fragments and figures FIRST (PYTHONPATH=src python experiments/make_figures.py &&
# ... meta_analysis.py) so the package reflects the committed results (R1/R2). Run from the paper/ dir.
set -euo pipefail
cd "$(dirname "$0")"
OUT=submission
rm -rf "$OUT"
mkdir -p "$OUT/figures"

# manuscript (self-contained; bibliography inlined in main.tex)
cp main.tex "$OUT"/
# the Scientific Reports class + its required dependencies. wlscirep.cls / naturemag-doi.bst pull in
# jabbrv (journal-name abbreviations); the SR online compiler does not provide it, so it must be bundled
# (jabbrv.sty + its two LTWA data files), exactly as in the working ns-defer SR submission.
# naturemag-doi.bst and refs.bib are kept only to regenerate the inlined bibliography (not compiled).
cp wlscirep.cls naturemag-doi.bst refs.bib \
   jabbrv.sty jabbrv-ltwa-all.ldf jabbrv-ltwa-en.ldf "$OUT"/

# auto-generated table fragments (regenerated from the committed CSVs; main uses 5, supplementary 2)
for f in datasets_table headline_table new_axes_table meta_table recalibration_table \
         per_dataset_table silent_cells; do
  cp "$f.tex" "$OUT"/
done

# figures referenced by \includegraphics (the pipeline figure is inline TikZ, no asset needed)
cp figures/reduction_curves.pdf figures/meta_harm.pdf "$OUT/figures"/

# compile offline (pdflatex only -- references are inlined, no bibtex) to verify self-containment
cd "$OUT"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
undef=$(grep -ic "undefined \(reference\|citation\)" main.log || true)
over=$(grep -c "Overfull .hbox" main.log || true)
pages=$(pdfinfo main.pdf 2>/dev/null | awk '/Pages/{print $2}')
echo "built submission/main.pdf (${pages} pp, undefined: ${undef}, overfull-hbox: ${over})"
# strip build by-products (keep sources + the compiled PDF)
rm -f ./*.aux ./*.blg ./*.log ./*.out ./*.spl
# assemble the upload ZIP: all LaTeX sources + assets the SR compiler needs (exclude the compiled PDF)
rm -f ns-clinical-fs.zip
zip -q ns-clinical-fs.zip main.tex wlscirep.cls naturemag-doi.bst refs.bib \
  jabbrv.sty jabbrv-ltwa-all.ldf jabbrv-ltwa-en.ldf \
  datasets_table.tex headline_table.tex new_axes_table.tex meta_table.tex recalibration_table.tex \
  per_dataset_table.tex silent_cells.tex figures/reduction_curves.pdf figures/meta_harm.pdf
echo "wrote submission/ns-clinical-fs.zip ($(unzip -l ns-clinical-fs.zip | tail -1 | awk '{print $2}') files)"
