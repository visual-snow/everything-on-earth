# DeepChem Capabilities

DeepChem is an open-source Python library for machine learning in drug discovery, quantum chemistry, materials science, and computational biology. It provides a unified API over TensorFlow, PyTorch, and JAX backends, with MoleculeNet as its integrated benchmark suite.

## Models

- Graph-based molecular models: GCN, GAT, MPNN, AttentiveFP, GROVER.
- Transformer-based molecular models: ChemBERTa, MolFormer.
- Quantum chemistry models: FermiNet, DTNN.
- Generative models: GAN, MolGAN, seq2seq.
- Scikit-learn model wrappers for classical baselines.

## Featurization

- Molecular fingerprints: circular (Morgan), MACCS keys, PubChem.
- Descriptor-based: RDKit descriptors, Mordred descriptors.
- Graph-based featurizers for graph convolutional networks.
- Coulomb matrices for quantum chemistry inputs.
- Featurizers for materials, biological sequences, and molecular images.

## Datasets

- MoleculeNet loaders cover toxicology (Tox21, MUV, ClinTox), bioactivity (HIV, BACE, BBBP, PCBA, ChEMBL), quantum chemistry (QM7, QM8, QM9), protein-ligand binding (PDBbind), and large-scale screening (ZINC15).
- Dataset splitters support random, scaffold, stratified, and other partitioning strategies.
- Data transformers handle normalization, balancing, and preprocessing.

## Molecular Docking

- Pose generation and scoring against target binding sites.
- Binding pocket detection.
- Docking engines are third-party; DeepChem provides the wrapping interface.

## Measurement

- Evaluation metrics include accuracy, AUC-ROC, RMSE, MAE, and R-squared.
- Weights and Biases integration is available for experiment tracking across training runs.

## Configuration

- Backend selection: TensorFlow, PyTorch, or JAX per model.
- GPU or CPU execution.
- Featurizer selection is model-dependent.
- Hyperparameter optimization is available as a first-class module.
- Dataset splitting strategy is configurable per experiment.

## Constraints

- Supports Python 3.7 through 3.10 only; Python 3.11 and later are not officially supported.
- Python scripting or notebooks are required; there is no GUI or no-code interface.
- Backend libraries and cheminformatics dependencies must be installed separately.
- The docking module wraps external engines and does not implement docking natively.
- No REST API, web service, or experiment tracking catalog is included.
- No native protein structure prediction capability.
