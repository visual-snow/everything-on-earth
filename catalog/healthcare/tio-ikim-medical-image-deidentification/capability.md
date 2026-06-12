# MEDE Capabilities

MEDE is a Python CLI and library for multi-step anonymization of medical imaging data. It combines DICOM metadata de-identification, facial feature removal (defacing), brain extraction (skull-stripping), and OCR-based burned-in text removal into a single pipeline. It also supports MRI raw data and whole slide image anonymization. Faster throughput than current state-of-the-art tools is claimed in the accompanying publication.

## DICOM Metadata

- Removes or modifies DICOM tags according to configurable confidentiality profiles based on the DICOM PS 3.15 standard
- Multiple profiles can be combined in a single run for layered de-identification

## Pixel-Level Anonymization

- Defacing removes facial features from head MRI and CT volumes to prevent facial reconstruction
- Skull-stripping extracts a brain mask and removes all non-brain tissue; runs on GPU for acceleration
- OCR-based text removal detects and blacks out burned-in patient identifiers in image pixels
- An interactive refinement mode allows manual bounding-box selection for pixel regions that automated detection missed

## Additional Formats

- MRI raw data anonymization handles Siemens twix format files
- Whole slide image anonymization processes pathology imaging data

## Pipeline

- Any combination of anonymization steps can be composed in a single run via CLI flags
- Multiprocessing distributes work across available CPU cores for batch throughput
- Container images are published for both x86_64 and ARM architectures

## Constraints

- GPU required for skull-stripping; may fail on CPU-only hosts
- OCR text removal depends on EasyOCR; not a pure-Python dependency
- Interactive refinement requires a graphical display environment; unsuitable for headless servers without X forwarding
- Operates on local filesystem only; no DICOM network protocol support for C-STORE or C-MOVE
- No audit log or provenance record of which tags or pixel regions were modified
- No FHIR, HL7, or HIPAA/GDPR compliance certification documentation
