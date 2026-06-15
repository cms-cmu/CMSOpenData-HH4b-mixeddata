
# CMSOpenData-HH4b-mixeddata

## Overview

This repository contains early workflow development for preparing and validating Jet-only derived datasets from CMS HH4b mixeddata ROOT files.

The current focus is to extract Jet-related variables from CMS Run 2 mixeddata samples for 2016, 2017, and 2018. The extracted Jet variables are saved as chunked Parquet files so they can be used more easily in downstream Python analysis workflows.

This work supports the broader goal of preparing a public, documented, and reproducible mixeddata benchmark for CMS HH4b background modeling studies.

## Current Workflow

The workflow currently does the following:

1. Opens CMS HH4b mixeddata ROOT files with `uproot`.
2. Inspects the `Events` TTree.
3. Finds Jet-related branches automatically.
4. Extracts:

   * `nJet`
   * all branches starting with `Jet_`
5. Saves Jet-only data as chunked Parquet files.
6. Validates that the Parquet files can be read back correctly.
7. Confirms that event counts match the original ROOT files.

## Repository Structure

```text
metadata/
    branches_mixed2016.txt
    branches_mixed2017.txt
    branches_mixed2018.txt
    jet_branches_mixed2016.txt
    jet_branches_mixed2017.txt
    jet_branches_mixed2018.txt
    jet_branches_mixed2016_with_types.txt
    jet_branches_mixed2017_with_types.txt
    jet_branches_mixed2018_with_types.txt

notes/
    week1_setup.md
    jet_extraction_summary.md

scripts/
    extract_jets.py
    extract_jets_2016.py
    extract_jets_2016_full.py
    validate_jet_outputs.py

outputs/
    jets/
        2016/
        2017/
        2018/
```

The `outputs/` directory contains generated Parquet files. These files are not committed to GitHub because they are generated data products and are ignored by `.gitignore`.

## Input ROOT Files

The current workflow uses the following CMS HH4b mixeddata ROOT files:

| Year | Input ROOT File                                                                                                                |
| ---- | ------------------------------------------------------------------------------------------------------------------------------ |
| 2016 | `root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2016_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root` |
| 2017 | `root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2017_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root` |
| 2018 | `root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2018_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root` |

## Environment Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install required Python packages:

```bash
python -m pip install --upgrade pip
python -m pip install uproot awkward numpy pyarrow coffea xrootd fsspec-xrootd
```

## Running on the Cluster

Light tasks such as editing files, checking Git status, and writing notes can be done on the Falcon head node.

Data processing should be done on a Slurm compute node. Start an interactive compute session with:

```bash
srun --mem=4G --time=04:00:00 --pty bash
```

Then return to the project directory and activate the environment:

```bash
cd ~/pursue2026/CMSOpenData-HH4b-mixeddata
source .venv/bin/activate
```

## Jet Extraction

The main scalable extraction script is:

```text
scripts/extract_jets.py
```

Run the extraction for a specific year:

```bash
python scripts/extract_jets.py --year 2016
python scripts/extract_jets.py --year 2017
python scripts/extract_jets.py --year 2018
```

For a small test run, use `--max-parts`:

```bash
python scripts/extract_jets.py --year 2016 --max-parts 1
```

This processes only the first chunk and is useful for testing.

## Branch Selection

The extraction keeps:

```text
nJet
all branches starting with Jet_
```

This produced 38 Jet-related branches for each year.

The Jet branch lists are saved in:

```text
metadata/jet_branches_mixed2016.txt
metadata/jet_branches_mixed2017.txt
metadata/jet_branches_mixed2018.txt
```

The Jet branch lists for 2016, 2017, and 2018 were compared with `diff`, and no differences were found.

## Extraction Results

| Year | Events in ROOT File | Jet Branches Extracted | Parquet Parts Written | Validation |
| ---- | ------------------: | ---------------------: | --------------------: | ---------- |
| 2016 |             115,764 |                     38 |                     3 | Passed     |
| 2017 |             111,951 |                     38 |                     3 | Passed     |
| 2018 |             162,896 |                     38 |                     4 | Passed     |

Total extracted events across all three years:

```text
390,611
```

## Output Files

The Jet-only Parquet files are saved locally under:

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

## Validation

The validation script is:

```text
scripts/validate_jet_outputs.py
```

Run:

```bash
python scripts/validate_jet_outputs.py
```

The script checks that:

1. Parquet files exist for each year.
2. Each Parquet file can be read with Awkward Array.
3. Each file has 38 Jet fields.
4. The total number of events read from Parquet matches the original ROOT file event count.

Current validation result:

```text
All Jet Parquet outputs passed validation.
```

## Current Status

Completed so far:

* Set up repository structure.
* Created Python environment.
* Opened and inspected the 2016 ROOT file.
* Saved branch metadata for 2016, 2017, and 2018.
* Built a scalable Jet extraction script.
* Extracted Jet-only Parquet files for 2016, 2017, and 2018.
* Validated all Jet-only Parquet outputs.
* Documented the extraction workflow and results.

## Next Steps

Potential next steps include:

1. Add more dataset files beyond the first mixeddata file per year.
2. Generalize the workflow to handle multiple files per year.
3. Add summary plots for Jet variables such as `Jet_pt`, `Jet_eta`, and `nJet`.
4. Compare distributions across 2016, 2017, and 2018.
5. Prepare additional documentation for public release and reproducibility.
