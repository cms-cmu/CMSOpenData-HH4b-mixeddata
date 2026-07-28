# Dependency Notes

## Current Reference Workflow

Original command:

./run_container snakemake --snakefile src/classifier/workflow/Snakefile --configfile coffea4bees/classifier/config/workflows/HH4b_2024_v2/SvB/workflow_config.yml --jobs 1

## Required Workflow Files

- workflow_config.yml
- train.yml
- evaluate.yml
- parent common.yml

## Main Model Modules

- HCR.SvB.ggF.baseline.Train
- HCR.SvB.ggF.baseline.Eval

## Main Dataset Modules

- HCR.SvB.Background
- HCR.SvB.Signal
- HCR.SvB.Eval

## Required Test Mode

--test-files is implemented by the ROOT dataset loader and limits ROOT inputs for quick testing.

Standalone development tests must use:

--test-files 2

## GPU Requirement

The Snakemake workflow uses:

gres = mps:25

for train/evaluate jobs.

## Independence Targets

The standalone workflow should not rely on these runtime paths:

- coffea4bees/classifier/config/workflows/
- coffea4bees/metadata/
- coffea4bees/analysis/weights/
- Alejandro's EOS output area

The standalone workflow may still use the same container at first.
