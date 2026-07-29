# HCR Classifier Scope: SvB and FvT

## Conclusion

The standalone HCR codebase is not limited to SvB classification. It contains shared HCR infrastructure and concrete dataset, training, loss, ROC, evaluation, and output implementations for both SvB and FvT.

SvB currently has complete, tested standalone Snakemake workflows. FvT is supported through reusable dataset and model components, but it does not yet have dedicated workflow YAML files or end-to-end validation.

## SvB support

Dataset configuration:

- `src/classifier/config/dataset/HCR/SvB.py`
- Classes: `_Train`, `Background`, `Signal`, and `Eval`

Model configuration:

- `src/classifier/config/model/HCR/SvB/ggF/baseline.py`
- Classes: `Train` and `Eval`
- Core implementation: `src/classifier/config/model/HCR/SvB/ggF/all_kl.py`

Standalone workflows:

- `configs/workflows/SvB/`
- `configs/workflows/SvB_week5_parquet_smoke/`
- `configs/workflows/SvB_week5_parquet_full/`

These workflows provide training, evaluation, k-fold merging, model outputs, and documented execution commands.

## FvT support

Dataset configuration:

- `src/classifier/config/dataset/HCR/FvT.py`
- Classes: `Train`, `TrainBaseline`, and `Eval`

Model configuration:

- `src/classifier/config/model/HCR/FvT/baseline.py`
- Classes: `Train` and `Eval`

The FvT implementation provides dataset selection, class labels, preprocessing, custom loss behavior, ROC definitions, evaluation outputs, and the final FvT prediction calculation.

## Shared HCR infrastructure

Both classifiers use:

- `src/classifier/config/model/HCR/_HCR.py`
- `HCRTrain`
- `HCREval`

This shared layer provides the HCR architecture, training and evaluation behavior, scheduling, model persistence, and k-fold support.

## Missing FvT workflow work

The repository does not currently contain:

- `configs/workflows/FvT/workflow_config.yml`
- `configs/workflows/FvT/train.yml`
- `configs/workflows/FvT/evaluate.yml`

A complete FvT workflow would still require:

- FvT-specific workflow YAML files
- Input metadata and friend mappings
- Training and evaluation parameters
- CPU smoke testing
- Production training validation
- Inference-output validation
- K-fold merge validation
- Portable-path checks
- User documentation

## Poster wording

The extracted HCR framework supports both SvB and FvT classification. This work establishes a tested standalone SvB training and inference workflow, while FvT remains a future integration target requiring dedicated workflow configuration and end-to-end validation.
