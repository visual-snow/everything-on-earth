# UMLS to SNOMED/ICD-10-CM Mapper Capabilities

This mapper is a Python script that reads UMLS Metathesaurus source files and generates JSON mapping files from UMLS Concept Unique Identifiers (CUIs) to SNOMED CT or ICD-10-CM codes. It supports three traversal strategies over the Metathesaurus graph. Configuration is hard-coded in the source file; there are no CLI flags or configuration files.

## Mapping Methods

- Exact match resolves CUIs to target codes by direct string and atom correspondence within UMLS; requires only the concept file
- Related Other (RO) traversal follows broad relationship links in the relationship file to find target codes connected to each CUI
- Parent-child (PAR_CHD) traversal walks the hierarchical relationship graph to discover codes at neighboring levels of the terminology tree

## Output

- Produces JSON files mapping each resolved CUI to one or more SNOMED CT or ICD-10-CM codes
- Separate output files are generated per mapping method and target terminology

## Constraints

- Requires an NLM UMLS license and manual download of MRCONSO.RRF and MRREL.RRF before use
- All configuration (file paths, mapping method) is hard-coded in the script; editing source code is required to change behavior
- The RO and PAR_CHD methods require the relationship file in addition to the concept file; the exact method uses only the concept file
- No CLI argument parsing, Docker image, pip package, or requirements file is provided
- No reverse mapping from SNOMED CT or ICD-10-CM back to UMLS CUIs
- No automated test suite or license file
