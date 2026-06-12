# OCL Mapper Capabilities

OCL Mapper is a collaborative web application (beta) for mapping spreadsheet-based source terminologies to standard target terminologies such as LOINC, CIEL, and ICD-10 stored in an OCL Terminology Server. It uses an AI-assisted matching algorithm based on vector embeddings and nearest-neighbor search to generate and rank mapping candidates. The matching engine runs on the external OCL Terminology Server, not within the mapper itself.

## Mapping Workflow

- Users upload a source terminology spreadsheet and select a target terminology from the OCL server
- The AI matching algorithm generates ranked candidate mappings for each source term
- Mappers review, accept, modify, or reject each suggested mapping through the web interface
- Mapped results can be exported back to the OCL Terminology Server

## AI-Assisted Matching

- Vector-embedding-based candidate generation produces ranked suggestions for each source term
- Benchmarking shows approximately 60% improvement in top-5 accuracy compared to standard string matching on CIEL datasets
- A command-line evaluation script measures matching accuracy and latency against a ground-truth spreadsheet column

## Authentication

- Single sign-on via an external identity provider is available as an optional deployment overlay
- Standard access does not require SSO

## Constraints

- Requires a running OCL Terminology Server; the AI matching algorithm is not embedded in the mapper
- Cross-origin policy must be explicitly configured to match the terminology server endpoint in production
- The evaluation script requires a ground-truth mapping decision column in the input spreadsheet
- No embedded NLP or vector search engine; all candidate generation is delegated externally
- No offline mode, audit log, or approval workflow documented
