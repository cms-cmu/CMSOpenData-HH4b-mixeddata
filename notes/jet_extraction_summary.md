# Jet Extraction Summary

## Purpose

The goal of this step was to extract only the Jet-related variables from the CMS HH4b mixeddata ROOT files and save them in a smaller, easier-to-use format.

The original ROOT files contain many branches. For this first extraction task, I focused only on:

* `nJet`
* all branches starting with `Jet_`

These variables were saved as chunked Parquet files for easier downstream analysis with Python tools such as Awkward Array, PyArrow, and Coffea.

## Input ROOT Files

The extraction was performed on the mixeddata ROOT files for Run 2 years 2016, 2017, and 2018.

| Year | Input ROOT File                                                                                                                |
| ---- | ------------------------------------------------------------------------------------------------------------------------------ |
| 2016 | `root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2016_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root` |
| 2017 | `root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2017_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root` |
| 2018 | `root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2018_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root` |

## Script Used

The scalable extraction script is:

```text
scripts/extract_jets.py
```

Example commands:

```bash
python scripts/extract_jets.py --year 2016
python scripts/extract_jets.py --year 2017
python scripts/extract_jets.py --year 2018
```

The script accepts a `--year` argument, selects the correct ROOT file, finds Jet branches automatically, saves metadata, extracts the Jet branches in chunks, and writes the output to Parquet files.

## Branch Selection

The script selected branches using the following rule:

```text
Keep nJet
Keep every branch that starts with Jet_
```

This produced 38 Jet-related branches for each year.

The Jet branch lists were saved in:

```text
metadata/jet_branches_mixed2016.txt
metadata/jet_branches_mixed2017.txt
metadata/jet_branches_mixed2018.txt
```

The branch lists were compared with `diff`, and no differences were found between the Jet branch lists for 2016, 2017, and 2018.

## Extraction Results

| Year | Total Events in ROOT File | Jet Branches Extracted | Parquet Parts Written | Verification |
| ---- | ------------------------: | ---------------------: | --------------------: | ------------ |
| 2016 |                   115,764 |                     38 |                     3 | Passed       |
| 2017 |                   111,951 |                     38 |                     3 | Passed       |
| 2018 |                   162,896 |                     38 |                     4 | Passed       |

Total events extracted across all three years:

```text
390,611 events
```

## Output Location

The generated Parquet files were saved locally under:

```text
outputs/jets/2016/
outputs/jets/2017/
outputs/jets/2018/
```

Example output files:

```text
outputs/jets/2016/jets_2016_part0000.parquet
outputs/jets/2017/jets_2017_part0000.parquet
outputs/jets/2018/jets_2018_part0000.parquet
```

The Parquet files are generated data products and are not committed to GitHub. They are ignored by `.gitignore`.

## Verification

For each year, the script compared:

```text
total events saved to Parquet
```

against:

```text
total events in the original ROOT file
```

The verification passed for all three years.

This confirms that the Jet-only extraction preserved the full event count for each dataset year while reducing the data to the selected Jet-related branches.

## Notes

This extraction was done on a Slurm compute node, not directly on the Falcon head node. This follows the correct workflow for processing data on the cluster.

The current workflow successfully creates a smaller Jet-only dataset from the CMS HH4b mixeddata ROOT files and prepares the data for future analysis steps.
