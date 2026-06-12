# GT4SD Molecular Design Capabilities

GT4SD Molecular Design is a seven-step computational pipeline for target-based drug discovery. It chains generative deep learning models with virtual screening and cloud-based retrosynthesis to produce synthesizable candidate molecules for a given protein target. All steps are run as individual Python scripts with no web UI or REST API.

## Data Preparation

- Retrieves binding affinity records (IC50/Ki) from a public database by protein target identifier
- Splits data into training and validation sets with binary activity labels at a configurable cutoff

## Virtual Screening

- A transformer-based model is trained on labelled binding affinity data to score candidate molecules against the target protein
- The trained model produces continuous affinity probability scores for filtering generated compounds

## Molecular Generation

- A substructure-driven graph generative model extends molecular scaffolds by adding structural motifs
- Generation can be seeded with curated active compounds to bias toward desired substructures, or run unbiased with a diverse seed set
- A sequence regression model optimizes the drug-likeness of generated molecules while maintaining structural validity

## Property Assessment

- Physicochemical properties including logP, molecular weight, ring counts, and quantitative drug-likeness score are computed for all candidates

## Retrosynthesis

- A cloud retrosynthesis service predicts multi-step synthesis routes for selected candidates
- The number of retrosynthesis steps and per-molecule timeout are configurable
- Requires an external account and API key

## Constraints

- The retrosynthesis service requires a free account, API key, and pre-created project on the external platform
- Generation quality depends on the size and quality of the seed molecule file
- The pipeline is strictly sequential; each step depends on output files from the previous step with hard-coded intermediate paths
- Conda environment setup involves a dependency conflict that requires a manual reinstall workaround
- No docking or physics-based binding simulation; affinity is predicted, not calculated
- No ADMET modelling beyond logP and drug-likeness score
- No containerized execution, web UI, or REST API
