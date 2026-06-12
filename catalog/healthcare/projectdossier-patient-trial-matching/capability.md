# Patient-Trial Matching Capabilities

This pipeline matches patient descriptions to clinical trials using a two-stage approach: NER-based data enrichment of disease and drug mentions followed by BERT cross-encoder neural re-ranking. It is evaluated on TREC Clinical Decision Support benchmarks and published in the Journal of Biomedical Informatics (2023). All interaction is script-based; no REST API or web interface is provided.

## Retrieval

- A lexical first stage (BM25/BM25+) retrieves candidate trials from a preprocessed ClinicalTrials.gov corpus
- Entity extraction identifies disease and drug mentions in patient descriptions to enrich query terms
- Custom age and gender NER models enable eligibility-based postprocessing filters on retrieved candidates

## Re-Ranking

- A BERT cross-encoder re-ranker is trained on topical relevance between patient descriptions and trial documents
- Further fine-tuning on eligibility criteria structure adapts the model to the specific information architecture of clinical trials
- Re-ranking is applied to the candidate set produced by the lexical retrieval stage

## Evaluation

- Precision at k is the primary evaluation metric, with reported improvements of 15% over lexical baselines
- Binary and graded relevance judgments from TREC-CDS 2021 and 2022 benchmark sets are used for evaluation
- Standard TREC submission file format enables comparison with other systems

## Constraints

- Requires manual download of ClinicalTrials.gov XML dumps from the TREC-CDS website; data is not bundled
- Trial preprocessing with entity extraction takes 5 to 10 hours on CPU across the full ClinicalTrials.gov corpus
- Locked to Python 3.8 with specific medspaCy 0.2.0.x and spaCy 3.1.6 versions; incompatible with newer releases
- Preparatory data fetch and age/gender model download must complete before any experiment can run
- No Docker, REST API, pre-built indices, or ClinicalTrials.gov API ingestion support
