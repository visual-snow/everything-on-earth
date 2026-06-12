# SlicerMONAIViz Capabilities

SlicerMONAIViz is a 3D Slicer extension that enables step-by-step execution and visualization of MONAI transform chains on medical images and labels. Users can inspect the output and data-dictionary statistics at every stage of the pipeline. It requires 3D Slicer as the host application and cannot run standalone.

## Transform Execution

- Runs a chain of MONAI transforms one step at a time over loaded medical image and label data
- Displays the transformed image and label output after each step for visual inspection
- Shows data-dictionary statistics at every stage to track how transforms modify the data

## Transform Chain Editing

- Imports pre-processing transform definitions directly from MONAI model zoo bundles
- Allows manual addition, removal, and reordering of transforms in the chain
- Supports building custom transform chains from scratch without a bundle

## Bundle Integration

- Loads transform definitions from published MONAI model zoo bundles by name
- Bridges the gap between MONAI training/inference configurations and interactive visualization in 3D Slicer

## Constraints

- Requires 3D Slicer version 5.3 or higher
- Depends on the PyTorch Slicer extension and MONAI Python packages with ITK and NiBabel extras
- Updating to a new plugin version may require reinstalling the 3D Slicer preview build
- No containerized deployment, REST API, or multi-user mode
- No CI or automated test harness
