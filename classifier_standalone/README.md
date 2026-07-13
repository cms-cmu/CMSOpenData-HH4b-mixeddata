# HH4b Classifier Standalone

Standalone repository for the HH4b SvB classifier training and evaluation workflow.

This repo separates the classifier workflow from the larger `barista` and `coffea4bees` analysis repositories. The goal is to run the classifier from a clean, independent repository and support a small training/evaluation smoke test using ROOT and Parquet friend inputs.

## Week 4 Goal

The Week 4 goal was to isolate the HH4b/SvB classifier code from the main analysis-specific repositories and prove that the workflow can run independently.

The mentor request was:

1. Do not run the full production job.
2. Run a small test using 2 files.
3. Convert ROOT friend trees into Parquet files.
4. Modify the code to read Parquet files instead of ROOT friend files.
5. Test again with a few events.

## What This Repo Does

This repo currently supports:

- Standalone SvB training smoke test
- Standalone SvB evaluation smoke test
- ROOT friend tree to Parquet conversion
- Parquet friend metadata generation
- Evaluation using Parquet friend inputs
- Writing ROOT SvB friend prediction outputs

## Week 4 Accomplishments

### 1. Created a standalone classifier repo

The classifier workflow now runs from:

`~/pursue2026/hh4b-classifier-standalone`

GitHub repo:

`https://github.com/IngFrancis/hh4b-classifier-standalone`

### 2. Built standalone CMU metadata

Standalone metadata was generated under:

- `configs/metadata/datasets_HH4b_Run2/2024_v2_cmu/`
- `configs/metadata/datasets_HH4b_Run2/2024_v2_cmu_eval2/`

Important files include:

- `classifier_inputs_week3_cmu.json`
- `classifier_inputs_week3_cmu_parquet.json`
- `fvt_inputs_week3_cmu.json`
- `fvt_inputs_week3_cmu_parquet.json`

### 3. Updated the SvB workflow configs

Updated files:

- `configs/workflows/SvB/train.yml`
- `configs/workflows/SvB/evaluate.yml`
- `configs/workflows/SvB/workflow_config.yml`

### 4. Verified standalone training

The standalone training smoke test completed and produced:

- `outputs/SvB_standalone_test/train.done`
- `outputs/SvB_standalone_test/classifier/result.json`
- `outputs/SvB_standalone_test/classifier/states.pkl`
- model `.pkl` files

### 5. Converted ROOT friend trees to Parquet

Scripts added:

- `scripts/convert_friend_root_to_parquet.py`
- `scripts/check_parquet_friends.py`
- `scripts/build_parquet_friend_metadata.py`

Parquet friend inputs were generated for `HCR_input` and `FvT_weight` using 100 events per file.

### 6. Added Parquet support

The reader was patched so `.parquet` friend paths can be read with `ak.from_parquet`.

Main file:

- `src/data_formats/root/io.py`

### 7. Fixed standalone smoke-test blockers

The evaluation path originally stalled during the standalone test. The fixes included:

- Avoiding remote ROOT metadata fetching for tiny smoke chunks
- Avoiding `ProcessPoolExecutor` when evaluating with one evaluator
- Adding Parquet friend input reading
- Adding runtime `pandas` support for Parquet-to-Pandas conversion
- Handling missing `p_ttbar` in tiny smoke-test model outputs

Important patched files:

- `src/classifier/config/dataset/_root.py`
- `src/classifier/config/main/evaluate.py`
- `src/classifier/config/model/HCR/SvB/ggF/all_kl.py`
- `src/data_formats/root/io.py`

### 8. Completed Parquet evaluation smoke test

Final test setup:

- 2 CMU input files
- 100 events per file

Input files:

- `data2016F/picoAOD.root`
- `data2016G/picoAOD.root`

Successful result:

- `exit_code=0`
- `outputs/SvB_standalone_test/evaluate.done`

The evaluation wrote two ROOT friend prediction chunks, each with 100 entries.

Output branches included:

- `q_1234`
- `q_1324`
- `q_1423`
- `p_multijet`
- `p_ttbar`
- `p_bkg`
- `p_ZZ`
- `p_ZH`
- `p_ggF`
- `p_sig`

## Verified Smoke-Test Path

ROOT friend trees were converted to Parquet friend files, the Parquet metadata was generated, the standalone Snakemake evaluation ran successfully, and ROOT SvB friend prediction chunks were written.

## What Is Not Claimed Yet

This is a smoke-test implementation, not a full production-scale run.

Not yet complete:

- Full production training over all files
- Full production evaluation over all files
- Removing or replacing `pyml.py`
- Full packaging as a polished long-term standalone library
- Large-scale benchmarking and physics validation

## Latest Verified Commit

`e187ab4 Add standalone Parquet SvB evaluation smoke test`

## Summary

The Week 4 milestone has been completed at smoke-test level. The classifier workflow is isolated in a standalone repository, training and evaluation work on a small 2-file test, ROOT friend trees were converted to Parquet, the code was modified to read Parquet inputs, and the few-event Parquet evaluation completes successfully.
