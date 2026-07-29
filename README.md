# HH4b HCR Classifier

A standalone and reproducible repository for training and evaluating the Hierarchical Combinatorial Residual classifier used in the CMS HH4b analysis.

The project isolates the classifier from the larger `barista` and `coffea4bees` analysis frameworks. It provides portable Pixi environments, standalone SvB workflows, and optional ROOT-to-Parquet preparation utilities.

## Current support

### SvB

The repository contains tested standalone SvB workflows for:

- CPU smoke-test training
- GPU full training
- CPU inference and evaluation
- Three-fold model handling
- Consolidated Parquet input reading
- ROOT friend prediction output

The full SvB training workflow has completed successfully on consolidated Parquet inputs. The current evaluation configuration has been validated with a bounded HH-only test.

### FvT

Reusable FvT dataset and model components are included:

- `src/classifier/config/dataset/HCR/FvT.py`
- `src/classifier/config/model/HCR/FvT/baseline.py`

The components import successfully and define FvT training, evaluation, loss, ROC, and output behavior.

A complete standalone FvT Snakemake workflow has not yet been assembled or validated.

> Current scope: tested end-to-end SvB workflows with reusable FvT components.

## Repository layout

- `src/` — classifier, data-loading, model, and workflow source code
- `configs/` — workflow, metadata, and weight configurations
- `tools/data_conversion/` — ROOT merging and ROOT-to-Parquet utilities
- `tools/legacy_jet_extraction/` — earlier jet-extraction scripts retained for reference
- `cluster/falcon/` — Falcon-specific submission files
- `cluster/run_container` — optional multi-site container wrapper
- `docs/` — project history, validation notes, and supporting documentation
- `outputs/` — generated models, predictions, logs, and converted datasets

The classifier is the repository's main focus. Data conversion, legacy extraction, historical documentation, and cluster-specific files are separated from the core classifier source.

## Environment setup

The repository uses Pixi for reproducible dependency management.

The `default` environment provides CPU-only PyTorch and supports data conversion, metadata generation, workflow dry-runs, smoke training, and CPU evaluation.

Install the CPU environment with:

    pixi install --environment default

The `gpu` environment targets CUDA 12.9 and is intended for full SvB training on a CUDA-capable compute node.

Install the GPU environment with:

    pixi install --environment gpu

The CPU and GPU dependencies are solved separately, so CPU-only systems do not require CUDA packages.

## Input data

The standalone workflows use consolidated Parquet datasets stored under:

    outputs/consolidated_production/

Each consolidated dataset combines synchronized information from:

- `picoAOD`
- `HCR_input`
- `JCM_weight`
- `FvT_weight`
- `SvB_MA`

The merger preserves all `Jet_*` branches and validates the required classifier and reference branches.

The active Parquet metadata is stored under:

    configs/metadata/datasets_HH4b_Run2/2024_v2_week5_parquet/

Metadata entries use repository-relative paths, for example:

    files:
      - outputs/consolidated_production/data2016F_UL16_postVFP_consolidated.parquet

## Data conversion

Data-conversion utilities are isolated under:

    tools/data_conversion/

They are optional preprocessing tools and are separate from the core classifier source.

Inspect the production dataset status with:

    pixi run --environment default conversion-dry-run

The current production map contains:

- 39 mapped datasets
- 38 eligible datasets
- 1 blocked dataset: `data2016G_UL16_postVFP`

Build all eligible consolidated ROOT and Parquet datasets with:

    pixi run --environment default python \
      tools/data_conversion/build_production_parquets.py

Merge one dataset with:

    pixi run --environment default python \
      tools/data_conversion/consolidate_dataset.py \
      GluGluToHHTo4B_cHHH1_UL18

Convert one consolidated ROOT file to Parquet with:

    pixi run --environment default python \
      tools/data_conversion/convert_dataset_to_parquet.py \
      outputs/consolidated_production/example_consolidated.root

Regenerate the portable Week 5 metadata with:

    pixi run --environment default python \
      tools/data_conversion/build_week5_parquet_metadata.py

## SvB smoke workflow

The smoke workflow uses CPU execution, bounded input chunks, one input file per dataset, and one training epoch.

Preview the workflow with:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1 \
      --dry-run

Run smoke training with:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_smoke/train.done

Run smoke evaluation with:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_smoke/evaluate.done

## Full SvB training

The full workflow uses:

- CUDA training
- 20 fixed-step epochs
- One fine-tuning epoch
- Three-fold model handling
- Consolidated Parquet signal and background inputs

Preview the full workflow from a CUDA-capable compute node with:

    pixi run --environment gpu snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_full/workflow_config.yml \
      --cores 1 \
      --dry-run

Run full training with:

    pixi run --environment gpu snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_full/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_full/train.done

The full training configuration is located at:

    configs/workflows/SvB_week5_parquet_full/train.yml

## Inference and evaluation

The validated evaluation configuration uses CPU execution and writes merged SvB friend predictions.

Run evaluation with:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_full/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_full/evaluate.done

The current full-workflow evaluation is intentionally bounded to:

- One HH input file
- Two input chunks
- 100 evaluation events

This validates the complete inference and friend-output path without claiming a full production-scale evaluation.

## Outputs

Training artifacts are written under:

    outputs/<workflow-label>/classifier/

Typical model files include:

- `result.json`
- `states.pkl`
- Model `.pkl` files

Evaluation friend outputs are written under:

    outputs/<workflow-label>/friend/

Prediction branches include:

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

Workflow completion flags and logs include:

- `train.done`
- `train.log`
- `evaluate.done`
- `evaluate.log`

## Cluster execution

The core classifier and data-conversion code use repository-relative paths and do not depend on Falcon-specific locations.

Optional cluster integration is isolated under:

    cluster/

Falcon-specific submission files are stored under:

    cluster/falcon/

The legacy multi-site container wrapper remains available at:

    cluster/run_container

Local Pixi execution is the portable default.

## Validation completed

The repository has been checked through:

- Python and shell syntax validation
- CPU PyTorch environment testing
- CUDA 12.9 lock inspection
- FvT component import testing
- Portable metadata validation
- Conversion command-interface testing
- Production conversion dry-run
- Jet-branch preservation checks
- SvB smoke training
- SvB full training
- Bounded SvB evaluation

## Current limitations

- A complete standalone FvT workflow has not been assembled or validated.
- `data2016G_UL16_postVFP` remains blocked in the production conversion map.
- Full production evaluation over every dataset has not yet been run.
- Cluster wrappers are retained as optional compatibility tools.

## Repository

    https://github.com/cms-cmu/CMSOpenData-HH4b-mixeddata
