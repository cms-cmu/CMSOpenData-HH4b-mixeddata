# Standalone HCR Classifier Workflow

This directory contains the Snakemake workflow used to train and evaluate standalone HCR classifiers.

Each run is controlled by:

- `workflow_config.yml`
- `train.yml`
- `evaluate.yml`

Ready-to-use standalone SvB configurations are located under:

- `configs/workflows/SvB/`
- `configs/workflows/SvB_week5_parquet_smoke/`
- `configs/workflows/SvB_week5_parquet_full/`

## Workflow structure

The main execution order is:

    train
      ├── evaluate
      ├── analyze
      ├── plot_inputs_raw
      ├── plot_inputs_dataprep
      └── plot_weights

Evaluation and analysis depend on completed training. Input and weight plotting rules run only when enabled in `workflow_config.yml`.

## Running the workflow

Run commands from the repository root.

Preview the smoke workflow without executing it:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1 \
      --dry-run

Run the complete smoke workflow:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1

Run smoke training only:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_smoke/train.done

Run smoke evaluation after training:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_smoke/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_smoke/evaluate.done

## Full GPU training

The full SvB workflow uses the `gpu` Pixi environment and CUDA-enabled training.

Run full training from a CUDA-capable compute node:

    pixi run --environment gpu snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_full/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_full/train.done

The full workflow evaluation configuration uses CPU execution:

    pixi run --environment default snakemake \
      --snakefile src/classifier/workflow/Snakefile \
      --configfile configs/workflows/SvB_week5_parquet_full/workflow_config.yml \
      --cores 1 \
      outputs/SvB_week5_parquet_full/evaluate.done

The training and evaluation settings are defined in:

- `configs/workflows/SvB_week5_parquet_full/train.yml`
- `configs/workflows/SvB_week5_parquet_full/evaluate.yml`
- `configs/workflows/SvB_week5_parquet_full/workflow_config.yml`

## Workflow configuration

Each `workflow_config.yml` file defines the paths and labels used by the Snakefile.

Important keys include:

- `classifier_config_paths` — value assigned to `CLASSIFIER_CONFIG_PATHS`
- `wfs_base` — directory containing `train.yml` and `evaluate.yml`
- `label` — name used to identify the workflow run
- `output_dir` — location for logs and completion flags
- `model` — model output directory
- `friend` — prediction friend-output directory
- `train_template` — parameters applied to the training configuration
- `eval_template` — parameters applied to the evaluation configuration
- `metadata` — classifier metadata used by optional plotting rules

Optional workflow features include:

- `plot_inputs`
- `plot_weights`
- `plot_base`

Changing the workflow `label`, model path, and output directory allows multiple runs to be kept separately.

## Classifier execution

The Snakefile invokes the standalone entry point:

    src/pyml.py

For each rule, the workflow supplies:

- The training or evaluation YAML configuration
- The shared `configs/workflows/common.yml` configuration
- Template parameters from `workflow_config.yml`
- Monitoring settings
- Multiprocessing settings
- The `CLASSIFIER_CONFIG_PATHS` environment variable

Successful training creates:

- `<output_dir>/train.done`
- `<output_dir>/train.log`
- `<model>/result.json`
- `<model>/states.pkl`
- Model `.pkl` files

Successful evaluation creates:

- `<output_dir>/evaluate.done`
- `<output_dir>/evaluate.log`
- Prediction files under the configured friend-output directory

## CPU and GPU environments

Use the `default` Pixi environment for:

- Workflow dry-runs
- CPU smoke training
- CPU evaluation
- Plotting and diagnostics

Use the `gpu` Pixi environment for full CUDA training.

## FvT status

The source tree includes importable FvT dataset and model implementations. However, the repository does not yet include a complete standalone FvT combination of:

- `workflow_config.yml`
- `train.yml`
- `evaluate.yml`

The ready-to-use workflows currently provided under `configs/workflows/` are SvB workflows.
