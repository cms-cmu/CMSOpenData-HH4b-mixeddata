# Project Checkpoint Summary

## Purpose

This checkpoint summarizes the current progress of the CMS Open Data HH4b mixeddata workflow.

The goal so far has been to prepare a clean, documented Jet-only derived dataset from the CMS HH4b mixeddata ROOT files, validate the extracted outputs, and create basic summary plots for first-pass inspection.

## Current Repository

Repository:

```text
https://github.com/cms-cmu/CMSOpenData-HH4b-mixeddata
```

Working directory on the cluster:

```text
~/pursue2026/CMSOpenData-HH4b-mixeddata
```

## Input ROOT Files

The workflow uses mixeddata ROOT files for Run 2 years 2016, 2017, and 2018.

### 2016

```text
root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2016_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root
```

### 2017

```text
root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2017_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root
```

### 2018

```text
root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2018_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root
```

## Branch Selection

The current derived dataset keeps only Jet-related branches.

The selected branches are:

```text
nJet
Jet_*
```

This includes the event-level jet count variable `nJet` and all branches beginning with `Jet_`.

Each year contains:

```text
38 Jet-related fields
```

## Extracted Event Counts

The extraction successfully produced Jet-only Parquet files for all three Run 2 years.

| Year  |  Events |
| ----- | ------: |
| 2016  | 115,764 |
| 2017  | 111,951 |
| 2018  | 162,896 |
| Total | 390,611 |

## Main Scripts Created

### Jet extraction script

```text
scripts/extract_jets.py
```

This script extracts Jet-related branches from the mixeddata ROOT files and writes them to Parquet files by year.

Example usage:

```bash
python scripts/extract_jets.py --year 2016
python scripts/extract_jets.py --year 2017
python scripts/extract_jets.py --year 2018
```

### Validation script

```text
scripts/validate_jet_outputs.py
```

This script checks that the Jet-only Parquet files can be read successfully, have the expected number of fields, and contain the expected event counts.

Example usage:

```bash
python scripts/validate_jet_outputs.py
```

### Plotting script

```text
scripts/plot_jet_summaries.py
```

This script creates normalized summary plots for basic Jet variables across 2016, 2017, and 2018.

Example usage:

```bash
python scripts/plot_jet_summaries.py
```

## Output Files

The Jet-only Parquet outputs are stored locally under:

```text
outputs/jets/2016/
outputs/jets/2017/
outputs/jets/2018/
```

These files are not committed to GitHub because they are derived data products.

The `.gitignore` file prevents large output files from being committed.

## Metadata Files

Branch metadata files were saved under:

```text
metadata/
```

These metadata files document the available branches and selected Jet-related branches for each year.

## Validation Status

Validation has passed for all three years.

The validation confirmed:

* All Parquet files can be opened.
* Each year has 38 Jet-related fields.
* The total event counts match the expected values.
* The derived Jet-only outputs are readable and usable for downstream analysis.

## Summary Plots

Jet summary plots were created under:

```text
plots/jets/
```

Current plots include:

```text
plots/jets/njet_by_year.png
plots/jets/jet_pt_by_year.png
plots/jets/jet_eta_by_year.png
```

These plots compare basic Jet distributions across 2016, 2017, and 2018.

The histograms are normalized so the shapes can be compared across years with different event counts.

## Documentation Created

The following documentation notes have been created:

```text
notes/week1_setup.md
notes/jet_extraction_summary.md
notes/jet_plot_summary.md
```

The README has also been updated with sections describing the extraction workflow, validation workflow, and Jet summary plots.

## Current Status

The project currently has:

* A working extraction pipeline for Jet-only data.
* Metadata documentation for selected Jet branches.
* Validated Parquet outputs for 2016, 2017, and 2018.
* Summary plots for basic Jet variables.
* GitHub-tracked scripts, metadata, plots, and documentation notes.

The local working tree was clean after the latest README update and push.

## Next Steps

Possible next steps include:

1. Add more summary plots for additional Jet variables.
2. Create ratio plots comparing 2017/2016 and 2018/2016.
3. Add event-selection checks if needed.
4. Compare Jet distributions in different regions or categories.
5. Prepare a short mentor-facing progress summary.
6. Begin planning the next derived dataset beyond Jet-only variables.
