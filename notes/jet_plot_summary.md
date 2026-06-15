# Jet Plot Summary

## Purpose

The goal of this step was to create quick summary plots from the Jet-only Parquet files produced during the extraction workflow.

These plots are intended as first-pass validation plots. They help confirm that the extracted Jet-only datasets can be read successfully and that basic Jet variables can be visualized across Run 2 years 2016, 2017, and 2018.

## Input Data

The plots were created using the Jet-only Parquet outputs stored locally under:

```text
outputs/jets/2016/
outputs/jets/2017/
outputs/jets/2018/
```

These Parquet files were generated from the CMS HH4b mixeddata ROOT files using:

```text
scripts/extract_jets.py
```

The validated event counts are:

| Year |  Events |
| ---- | ------: |
| 2016 | 115,764 |
| 2017 | 111,951 |
| 2018 | 162,896 |

## Plotting Script

The plotting script is:

```text
scripts/plot_jet_summaries.py
```

Run the script with:

```bash
python scripts/plot_jet_summaries.py
```

The script loads the Jet-only Parquet files for 2016, 2017, and 2018, then creates normalized histograms for selected Jet variables.

## Output Plots

The plots are saved in:

```text
plots/jets/
```

The generated plot files are:

```text
plots/jets/njet_by_year.png
plots/jets/jet_pt_by_year.png
plots/jets/jet_eta_by_year.png
```

## Variables Plotted

### `nJet`

`nJet` is the number of jets in each event.

This is an event-level variable, meaning each event has one `nJet` value.

The plot:

```text
plots/jets/njet_by_year.png
```

shows the distribution of the number of jets per event for 2016, 2017, and 2018.

### `Jet_pt`

`Jet_pt` is the transverse momentum of each jet.

This is a jet-level variable, meaning each event can contain multiple `Jet_pt` values because each event can have multiple jets.

Before plotting, the jagged `Jet_pt` arrays were flattened so that every jet contributes one value to the histogram.

The plot:

```text
plots/jets/jet_pt_by_year.png
```

shows the normalized Jet transverse momentum distribution for each year.

### `Jet_eta`

`Jet_eta` is the pseudorapidity of each jet.

This is also a jet-level variable, so the arrays were flattened before plotting.

The plot:

```text
plots/jets/jet_eta_by_year.png
```

shows the normalized Jet pseudorapidity distribution for each year.

## Why the Histograms Are Normalized

The histograms are normalized because each year has a different number of events:

| Year |  Events |
| ---- | ------: |
| 2016 | 115,764 |
| 2017 | 111,951 |
| 2018 | 162,896 |

Normalization lets us compare the shapes of the distributions across years without the year with more events automatically appearing larger.

## Current Status

The plotting workflow successfully:

* Loaded the Jet-only Parquet files for 2016, 2017, and 2018.
* Confirmed that each year has 38 Jet fields.
* Created summary plots for `nJet`, `Jet_pt`, and `Jet_eta`.
* Saved the plots as PNG files under `plots/jets/`.

These plots provide a first visual check that the Jet-only Parquet outputs are readable and usable for downstream analysis.

## Notes

These plots are validation-level plots, not final physics results.

More detailed follow-up work may include:

1. Adding ratio plots between years.
2. Checking additional Jet variables.
3. Comparing distributions before and after event selections.
4. Producing publication-style plots with CMS labeling.
5. Investigating any visible differences between years if needed.
