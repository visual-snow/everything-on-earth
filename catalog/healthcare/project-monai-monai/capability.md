# MONAI Capabilities

MONAI (Medical Open Network for AI) is a PyTorch-based framework for deep learning in medical image analysis. It provides domain-specific transforms, model architectures, loss functions, metrics, and training infrastructure for segmentation, classification, and detection tasks on clinical imaging data. MONAI does not include a DICOM server, model-serving endpoint, annotation tooling, or any HL7/FHIR interface.

Two execution modes:
- Interactive/scripted: models are built and trained programmatically using MONAI components within Python workflows.
- Bundle mode: config-driven portable workflows defined in JSON or YAML execute training or inference without custom code.

## Image Transforms

- Pre-processing covers intensity normalization, resampling, cropping, and spatial orientation correction for 3D medical volumes.
- Augmentation operations include random flips, rotations, elastic deformations, intensity shifts, and noise injection.
- Transforms compose into pipelines and can execute on CPU or GPU.
- Lazy resampling reduces redundant computation across chained spatial transforms.

## Model Architectures

- Purpose-built networks include UNet variants, SegResNet, DynUNet, SwinUETR, ViT, and attention-based backbones suited to volumetric imaging.
- Architectures support 2D, 3D, and pseudo-3D inputs.
- Pre-trained weights are available through the MONAI Model Zoo via the Bundle format.

## Training and Evaluation

- Supervised training loops run via an engine layer built on PyTorch Ignite, with event-driven handler callbacks.
- Loss functions include Dice loss, focal loss, and combined Dice-cross-entropy losses designed for class-imbalanced segmentation.
- Evaluation metrics cover Dice similarity coefficient, Hausdorff distance, mean IoU, surface distance, ROC AUC, and confusion matrix statistics.
- Multi-GPU and multi-node data parallelism are supported through standard PyTorch distributed training.

## Inference

- Sliding window inference tiles predictions across volumes larger than GPU memory and reassembles results.
- Patch-based and simple single-pass inference strategies are also available.
- Test-time augmentation can aggregate predictions across transformed inputs.

## Automated Segmentation

- Auto3DSeg runs an end-to-end automated pipeline for 3D segmentation: data analysis, algorithm selection, training, and ensembling.
- Reduces manual architecture and hyperparameter search for new segmentation tasks.

## Federated Learning

- Federated training coordinates model updates across sites without centralizing data.
- Compatible with NVIDIA FLARE as the federation backend.

## Constraints

- Requires Python 3.9 or later and PyTorch 2.4.1 or later; no support for older runtimes.
- Full performance requires an NVIDIA CUDA GPU; GPU-accelerated image I/O is Linux-only.
- No built-in DICOM networking or PACS connectivity; all imaging I/O depends on third-party libraries.
- The Bundle format is not interoperable with other model-serving standards out of the box.
- No built-in dataset registry, data versioning, or labeling interface.
