# SlicerOpenAnatomy Capabilities

SlicerOpenAnatomy is a 3D Slicer extension that exports segmentation and model hierarchy data to glTF or OBJ files compatible with the Open Anatomy Project browser. It also provides an atlas editor for merging or removing anatomical label groups from volumetric labelmaps. It requires 3D Slicer as a host application and cannot run standalone.

## Export

- Exports segmentation nodes or subject hierarchy folders to glTF, OBJ, or MRML scene format
- glTF output preserves model hierarchy, names, colors, and opacities using PBR materials
- OBJ output preserves color and transparency but does not retain hierarchy or model names
- Mesh decimation is configurable to reduce output geometry size
- Scene export writes models back into the Slicer session rather than to file

## Atlas Editing

- Loads an atlas from a volumetric labelmap paired with a color table and a JSON hierarchy schema
- Merges selected label groups into a single consolidated structure
- Removes selected label groups from the atlas

## Formats

- glTF (GL Transmission Format) as primary export target
- Wavefront OBJ as secondary export target
- NRRD volumetric labelmap as atlas input
- JSON hierarchy schema defining the anatomical grouping tree

## Constraints

- Requires 3D Slicer as the host application; no standalone or server-side execution
- glTF export converts shading to PBR, causing slight color and surface appearance differences versus Slicer display
- Atlas editor input must be a labelmap NRRD file paired with a color table and a JSON structure file; other volume types are not supported
- OBJ export loses hierarchy and model names
- No DICOM import or export within this extension
