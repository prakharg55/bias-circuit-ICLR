# Many Biases, One Circuit (ICLR 2027 submission)

## Layout
- `sycophancy_gain.tex`  - the paper (single file, main text + appendix)
- `sycophancy_gain.pdf`  - current compiled draft
- `references.bib`       - bibliography (all entries verified against arXiv/ACL/PMLR)
- `math_commands.tex`, `iclr2027_conference.sty/.bst`, `fancyhdr.sty`, `natbib.sty` - ICLR style
- `figures/`             - all figures included by the paper, plus `make_figs.py`,
                           which regenerates every generated figure directly from the
                           experiment artifacts in `../syco_circuit/results/`
- `figures/attic/`       - generated figures no longer included in the paper
- `attic/`               - old material kept for reference (template example, backups,
                           parked bib entries); `attic/logs/` and `attic/checks/` hold
                           historical build logs and page-render snapshots

## Build
pdflatex sycophancy_gain && bibtex sycophancy_gain && pdflatex sycophancy_gain && pdflatex sycophancy_gain

For Overleaf: upload the root .tex/.bib/.bbl, the four style files, math_commands.tex,
and the `figures/` folder (the `attic/` folders are not needed).
