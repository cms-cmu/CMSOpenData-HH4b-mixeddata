# Week 7 Repository Refactor Inventory

This directory records the repository changes made during the Week 7 classifier refactor.

The inventory compares:

    week6-pruned-parquet-schema...week7-repository-refactor

## Change summary

- Added paths: 5
- Modified paths: 2
- Deleted paths: 4
- Renamed or moved paths: 331
- Total path changes: 342

## Main destinations

- `src/` — 249 classifier and supporting source files
- `configs/` — 59 workflow, metadata, and weight files
- `tools/` — 16 conversion and legacy extraction scripts
- `docs/` — 4 historical and supporting documents
- `cluster/` — 2 cluster integration files
- `pixi.lock` — 1 relocated environment lock file

The full path-by-path inventory is available in:

    docs/week7/week7_file_inventory.tsv

Most Week 7 changes are file moves from the former `classifier_standalone/` directory into a classifier-centered top-level repository structure.

## Final validation

The refactored repository passed the following checks:

- Python syntax compilation completed with exit status 0.
- Six tracked shell and SLURM scripts passed `bash -n`.
- Forty-two active YAML files parsed successfully.
- No personal Falcon home paths remain in active reusable files.
- The SvB smoke workflow built a four-job Snakemake DAG: `train`, `evaluate`, `analyze`, and `all`.
- No hardcoded accelerator resources remain outside the site-specific `cluster/` directory.
- Git whitespace validation passed.

Python emitted non-fatal warnings for existing `\[` escape sequences in classifier help strings. These warnings did not prevent compilation.

## Created or relocated file paths

`created_file_paths.txt` lists the 337 files added or relocated into their final repository paths during the Week 7 refactor.

All listed paths were verified to exist, with no duplicate or missing entries.

## SvB and FvT classifier scope

The standalone HCR codebase supports both SvB and FvT classification.

SvB has complete, tested standalone training and evaluation workflows. FvT has functional dataset and model components, but still requires dedicated workflow YAML files and end-to-end validation.

The detailed technical review is available in:

    docs/week7/fvt_scope_review.md
