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
