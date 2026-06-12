# Sanger-ToL Variant Calling Capabilities

This pipeline is a Nextflow DSL2 workflow for variant calling on PacBio long-read data using DeepVariant. It produces per-sample VCF and GVCF outputs along with heterozygosity and nucleotide-diversity statistics. It accepts aligned or unaligned CRAM/BAM inputs alongside a reference FASTA and follows the nf-core module framework for containerized process execution.

## Variant Calling

- DeepVariant neural-network caller identifies SNPs and small indels from PacBio long reads
- Per-sample VCF and GVCF files are produced for downstream analysis or joint genotyping
- Calling can be restricted to specific genomic regions via a BED interval file

## Alignment

- An optional alignment mode maps raw reads to the reference genome using Minimap2 before calling
- PacBio vector contamination is screened using BLAST against a bundled vector database
- Alignment filtering removes secondary and supplementary alignments before variant calling

## Statistics

- VCFtools computes per-sample heterozygosity rate from the called variants
- Per-site nucleotide diversity is calculated across variant positions
- Position-level include and exclude filters can be applied before statistics computation

## Parallelization

- The reference genome is sharded by sequence for scatter-gather parallel execution of DeepVariant
- Each pipeline process runs in its own container via Docker, Singularity, Podman, or other supported runtimes

## Constraints

- Designed exclusively for PacBio long-read data; the DeepVariant model is PacBio-specific
- Requires Nextflow version 23.10.1 or later
- No joint genotyping across multiple samples; VCF merging is per-sample only
- No structural variant calling, short-variant phasing, or variant annotation/filtration steps
- The vector contamination database is a required runtime asset; offline runs must supply it explicitly
- CI is validated on LSF infrastructure; other schedulers require custom configuration profiles
