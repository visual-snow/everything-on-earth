# IMHOTEP Capabilities

IMHOTEP is a Unity3D-based VR framework for pre-operative surgical planning. It loads patient-specific DICOM scans and segmented 3D organ meshes into an immersive HTC Vive or Oculus Rift environment for interactive review by surgeons. Developed at the National Center for Tumor Diseases Dresden; research use only, not a medical product. Unmaintained since 2019.

## Visualization

- GPU-based volumetric rendering of CT and MRI scan stacks in transverse orientation
- 2D DICOM slice viewer for detailed cross-sectional image review
- Pre-segmented organ meshes displayed as interactive 3D objects
- Per-object transparency adjustment for layered anatomy exploration
- Predefined camera orientations for standardized organ views

## Annotation

- 3D and 2D annotation placement directly on anatomical structures within the VR scene
- Annotations are spatially anchored to patient anatomy

## Patient Data

- Patient case selector loads individual datasets including 3D models, DICOM slices, and clinical metadata
- Patient briefing displays case-specific clinical context including indication and medical history
- A non-VR mouse fallback mode operates without a headset for desktop review

## Constraints

- Requires an HTC Vive or Oculus Rift headset for full VR functionality
- Only Unity3D versions 2017.1 and 2017.2 are tested; newer versions are unsupported
- Blender3D is required for 3D asset preparation in the content pipeline
- Research use only under BSD license with no warranty; not a certified medical product
- Sagittal and coronal volumetric rendering is disabled due to incorrect orientation rendering
- DICOM 2D slice loading is blocked while a volume is loading; no concurrent queue
- Unmaintained since 2019; no multi-user mode, PACS integration, or containerized deployment
