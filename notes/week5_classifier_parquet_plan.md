# Week 5 Classifier Parquet Transition Plan

## Context

Week 4 was completed in the standalone classifier repository:

https://github.com/IngFrancis/hh4b-classifier-standalone

That repo isolates the HH4b/SvB classifier workflow from the original `barista + coffea4bees` setup and demonstrates a small standalone training/evaluation smoke test.

## Week 4 Completed Work

Completed before starting Week 5:

- Created a standalone HH4b/SvB classifier repository.
- Built standalone CMU metadata for the SvB workflow.
- Updated SvB training and evaluation configs.
- Verified the Snakemake training smoke test.
- Converted ROOT friend trees into Parquet files.
- Generated Parquet friend metadata.
- Patched the reader to support `.parquet` friend inputs through `ak.from_parquet`.
- Fixed evaluation blockers related to ROOT metadata fetching, single-worker multiprocessing, missing pandas import, and missing `p_ttbar`.
- Verified Parquet evaluation on 2 CMU files with 100 events per file.
- Confirmed evaluation wrote ROOT SvB friend prediction chunks with 100 entries each.

## Current Format Status

### Training

Current verified training path:

- Input: ROOT-based classifier/event/friend inputs referenced through JSON/YAML metadata configs.
- Output: JSON and PKL training/model artifacts.

Training outputs include:

- `result.json`
- `states.pkl`
- trained model `.pkl` files

### Evaluation

Current verified evaluation path:

- Base event references: ROOT `picoAOD.root` files.
- Friend inputs: Parquet files converted from ROOT friend trees.
- Output: ROOT SvB friend prediction trees.

The verified path is:

```text
ROOT friend trees
    -> Parquet friend files
    -> Parquet metadata
    -> standalone Snakemake evaluation
    -> ROOT SvB friend prediction chunks


```

## Week 5 Goals

The Week 5 goals are:

1. Upload recent progress to the private `cms-cmu/CMSOpenData-HH4b-mixeddata` repository.
2. Remove container dependency and run directly from a Pixi environment.
3. Move training and evaluation inputs and outputs toward Parquet.
4. Run full training using Parquet files for data, ttbar, ZH, HH, and ZZ.
5. Run a fast evaluation focused only on `GluGluToHHTo4B_cHHH1`.
6. Cross-check outputs against reference `SvB_weight` values.
7. Merge `picoAOD` branches and friend-tree branches into a single consolidated file before converting to Parquet.

## Open Questions for Mentor

1. Should `pyml.py` be removed entirely, or kept if the workflow runs correctly?
2. Should the final standalone interface be Snakemake-based, a direct Python CLI, or both?
3. Should evaluation output remain ROOT friend trees for compatibility, or should output also become Parquet?
4. Should training inputs be fully Parquet now, or is Week 5 mainly focused on evaluation and merged Parquet datasets?
5. Should base `picoAOD` branches and friend-tree branches be merged into one Parquet file per dataset/sample?
6. What tolerance should be used when comparing against reference `SvB_weight` values?
7. Should the standalone classifier repo remain separate, or should code be copied into this private mixeddata repo?

## Suggested Next Steps

1. Add or verify a Pixi environment in this repo.
2. Run commands without `run_container`.
3. Write a script to merge `picoAOD` branches and friend-tree branches.
4. Convert merged ROOT inputs into Parquet.
5. Start with a tiny Parquet training/evaluation test.
6. Scale up to full training on Falcon GPUs with `mps=25`.
7. Evaluate only `GluGluToHHTo4B_cHHH1`.
8. Compare outputs against reference `SvB_weight`.
