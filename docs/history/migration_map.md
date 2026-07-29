# Migration Map

This document tracks how the original barista + coffea4bees SvB workflow is moved into the standalone classifier repository.

| Original Path | New Path | Purpose | Status |
|---|---|---|---|
| barista/src/classifier/workflow/Snakefile | src/classifier/workflow/Snakefile | Snakemake train/evaluate workflow | TODO |
| barista/src/classifier/config/dataset/HCR/SvB.py | src/classifier/config/dataset/HCR/SvB.py | SvB dataset config: Background, Signal, Eval | TODO |
| barista/src/classifier/config/model/HCR/SvB/ggF/baseline.py | src/classifier/config/model/HCR/SvB/ggF/baseline.py | SvB baseline Train/Eval model config | TODO |
| barista/src/classifier/config/model/HCR/SvB/ggF/one_kl.py | src/classifier/config/model/HCR/SvB/ggF/one_kl.py | Baseline Train dependency | TODO |
| barista/src/classifier/config/model/HCR/SvB/ggF/all_kl.py | src/classifier/config/model/HCR/SvB/ggF/all_kl.py | Baseline Eval dependency | TODO |
| barista/src/classifier/config/model/HCR/SvB/arch/finetune_ggF.py | src/classifier/config/model/HCR/SvB/arch/finetune_ggF.py | SvB architecture/training dependency | TODO |
| barista/src/classifier/config/model/HCR/SvB/arch/reinterpret.py | src/classifier/config/model/HCR/SvB/arch/reinterpret.py | ROC/reinterpretation dependency | TODO |
| barista/coffea4bees/classifier/config/workflows/HH4b_2024_v2/SvB/workflow_config.yml | configs/workflows/SvB/workflow_config.yml | Workflow config | TODO |
| barista/coffea4bees/classifier/config/workflows/HH4b_2024_v2/SvB/train.yml | configs/workflows/SvB/train.yml | Training config | TODO |
| barista/coffea4bees/classifier/config/workflows/HH4b_2024_v2/SvB/evaluate.yml | configs/workflows/SvB/evaluate.yml | Evaluation config | TODO |
| barista/coffea4bees/classifier/config/workflows/HH4b_2024_v2/common.yml | configs/workflows/common.yml | Shared DataLoader/ROOT/HCR settings | TODO |
| barista/coffea4bees/metadata/datasets_HH4b_Run2/2024_v2/ | configs/metadata/datasets_HH4b_Run2/2024_v2/ | Input metadata | TODO |
| barista/coffea4bees/analysis/weights/JCM/2024_v2_nominal/jetCombinatoricModel_SB_2024_v2.yml | configs/weights/JCM/jetCombinatoricModel_SB_2024_v2.yml | JCM weights | TODO |
