# Raidionics-Slicer Capabilities

Raidionics-Slicer is a 3D Slicer extension that runs AI-based segmentation models and generates standardized clinical reports (RADS) for brain tumors and mediastinal structures from MRI volumes. All inference processing executes inside a Docker container; Docker Desktop must be installed and running. Only CPU execution is supported.

## Segmentation

- Automatic segmentation of brain tumors from MRI volumes using deep learning models
- Supports preoperative contrast-enhancing tumors (glioblastoma, meningioma) and postoperative residual tumor with cavity and FLAIR changes
- Mediastinum mode segments lymph nodes, airways, and anatomical structures
- Models are downloaded from GitHub Releases on first use

## Clinical Reporting

- Generates quantitative measurements including tumor volume, axis diameters, and equivalent diameters
- Reports laterality percentages and midline crossing status
- Calculates multifocality metrics including lesion count and maximum inter-lesion distance
- Computes resectability index, resectable volume, and expected residual volume
- Measures cortical and subcortical atlas overlap percentages against standard brain atlases

## Constraints

- Docker Desktop must be installed and running; no alternative processing path exists
- CPU-only execution is enforced; no GPU acceleration is available in the current container image
- Tested only on 3D Slicer versions 5.8.1 and 5.9.0; other versions are unsupported
- Models are downloaded at runtime on first use; the 3D Slicer UI becomes unresponsive during the pull
- No batch processing interface; one volume at a time through the GUI
- No DICOM structured report export; output is JSON and Slicer label maps
- Limited to brain CNS and mediastinum targets; no spine, prostate, or other organ support
