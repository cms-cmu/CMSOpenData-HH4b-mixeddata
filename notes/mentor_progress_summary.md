# Mentor Progress Summary

## Overview

This week, I focused on building the first working version of the Jet-only extraction and validation workflow for the CMS Open Data HH4b mixeddata project.

The main goal was to take the mixeddata ROOT inputs for Run 2 years 2016, 2017, and 2018, extract the Jet-related branches, save them into easier-to-use Parquet files, validate the outputs, and create basic summary plots.

## Completed Work

I created a reusable Jet extraction script:

```text
scripts/extract_jets.py
```

This script reads the mixeddata ROOT files, selects the Jet-related branches, and writes the extracted arrays into year-specific Parquet files.

The selected branches are:

```text
nJet
Jet_*
```

Each year contains 38 Jet-related fields.

## Extracted Data

The extraction was completed for all three Run 2 years:

| Year  |  Events |
| ----- | ------: |
| 2016  | 115,764 |
| 2017  | 111,951 |
| 2018  | 162,896 |
| Total | 390,611 |

The derived Parquet outputs are stored locally under:

```text
outputs/jets/2016/
outputs/jets/2017/
outputs/jets/2018/
```

These output files are ignored by Git because they are derived data products.

## Validation

I also created a validation script:

```text
scripts/validate_jet_outputs.py
```

The validation checks that:

* The Parquet files can be opened successfully.
* Each year contains the expected 38 Jet-related fields.
* The total event counts match the expected values.
* The extracted outputs are readable and usable for downstream analysis.

Validation passed for 2016, 2017, and 2018.

## Summary Plots

I created a plotting script:

```text
scripts/plot_jet_summaries.py
```

This script produces normalized summary plots for basic Jet variables across 2016, 2017, and 2018.

The current plots are:

```text
plots/jets/njet_by_year.png
plots/jets/jet_pt_by_year.png
plots/jets/jet_eta_by_year.png
```

These plots provide a first visual check of the extracted Jet-only datasets. The histograms are normalized so the distribution shapes can be compared across years with different event counts.

## Documentation

I added documentation notes to keep the workflow organized:

```text
notes/jet_extraction_summary.md
notes/jet_plot_summary.md
notes/project_checkpoint.md
```

I also updated the README to describe the extraction workflow, validation workflow, and Jet summary plots.

## Current Status

The repository now has:

* A working Jet-only extraction pipeline.
* Metadata files documenting the selected Jet branches.
* Validated Parquet outputs for 2016, 2017, and 2018.
* Summary plots for `nJet`, `Jet_pt`, and `Jet_eta`.
* Documentation explaining the workflow and current checkpoint.

Everything has been committed and pushed to GitHub.

## Next Steps

The next possible steps are:

1. Add more summary plots for additional Jet variables.
2. Create ratio plots comparing 2017/2016 and 2018/2016.
3. Add event-selection checks if needed.
4. Compare Jet distributions across different regions or categories.
5. Begin planning the next derived dataset beyond Jet-only variables.
