# PILOT (E3MolDiffusion) Capabilities

PILOT is an equivariant diffusion model for pocket-conditioned de novo 3D ligand generation. It combines continuous and discrete denoising diffusion with multi-objective importance sampling to guide generated molecules toward desired binding affinity and synthetic accessibility targets. Developed at Pfizer; model weights are not bundled and must be requested from the authors.

## Molecular Generation

- Generates 3D molecular structures conditioned on a protein binding pocket extracted from a co-crystal structure
- Equivariant architecture preserves rotational and translational symmetry of molecular coordinates
- Ligand size is sampled from a learned prior distribution or can be fixed to the ground-truth atom count
- Supports both CrossDocked2020 and Kinodata-3D training datasets

## Property Guidance

- Multi-objective importance sampling steers generation toward higher binding affinity scores
- Synthetic accessibility guidance biases generation toward more easily synthesizable molecules
- Property and SA guidance can be combined in a single sampling run with configurable weighting and scheduling

## Evaluation

- Generated molecules are scored via AutoDock Vina or QVina2 docking against the target pocket
- Predicted IC50 values provide a biological potency indicator for kinase targets
- RMSD against ground-truth ligand poses measures geometric accuracy
- Standard CrossDocked2020 benchmark metrics enable comparison with other structure-based drug design methods

## HPC Integration

- Multi-GPU sampling is orchestrated via SLURM job arrays for high-throughput generation
- Docking evaluation runs as parallel CPU jobs on cluster compute nodes
- Result aggregation scripts consolidate outputs across job arrays

## Constraints

- Model weights are not included in the repository; must be obtained by email from the authors
- Three separate conda environments are required to cover training, docking, and receptor preparation
- SLURM HPC cluster assumed for sampling and docking; no single-machine orchestration provided
- Pocket definition requires a reference ligand in the input structure; blind binding-site prediction is out of scope
- No REST API, web UI, or containerized deployment
