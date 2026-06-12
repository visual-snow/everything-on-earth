# RPTK Capabilities

RPTK (Radiomics Processing Toolkit) is an automated end-to-end pipeline for binary classification radiomics biomarker discovery. It covers image standardization, feature extraction, stability filtering, model training with cross-validation, and bootstrap evaluation with confidence intervals. Developed at the Division of Medical Image Computing at DKFZ.

## Feature Extraction

- Extracts radiomic features from medical images (CT and MR) in NIfTI or NRRD format using PyRadiomics and MIRP
- Image standardization and transformation normalize inputs before extraction
- Segmentation perturbation generates systematic mask variations to test feature robustness
- Connected-component artifact filtering removes extraneous mask regions before extraction

## Feature Selection

- Intraclass correlation coefficient filtering retains only features stable across segmentation perturbations
- Sequential forward and backward selection using random forest identifies the most informative feature subset
- Multi-rater mode filters features based on agreement across different raters' segmentations

## Model Training

- Six machine learning models are trained with cross-validation and ensemble averaging
- Model selection is based on validation AUROC across cross-validation folds
- Test AUROC with 95% confidence intervals is computed via 1000-iteration bootstrapping
- A Youden-index-optimized decision threshold maximizes the sum of sensitivity and specificity
- Learning curve analysis assesses dataset size adequacy

## Longitudinal Analysis

- A delta radiomics module computes feature differences across multiple timepoints for longitudinal studies

## Constraints

- Binary classification only; multi-class prediction and regression are not supported
- A minimum of approximately 120 samples is recommended for reliable model training
- Linux operating system required; Python 3.9, 3.10, or 3.11 supported
- Input images must be pre-converted to NIfTI or NRRD format; no direct DICOM ingestion
- Identifier column must not contain underscores; clinical parameter column names must not contain the substring "index"
- No active learning, uncertainty quantification beyond bootstrap CI, or Windows/macOS support
