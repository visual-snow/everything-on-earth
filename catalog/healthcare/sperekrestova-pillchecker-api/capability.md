# PillChecker API Capabilities

PillChecker API is a Python REST service that identifies drugs from OCR text using NER and RxNorm lookup, then checks pairwise drug-drug interactions against a vendored DrugBank database. It classifies interaction severity using a zero-shot language model with regex fallback. It is explicitly informational only; not a medical device or source of clinical advice.

## Drug Identification

- A 149-million-parameter NER model extracts drug entity mentions from input text
- Identified entities are normalized against the RxNorm terminology via the NLM REST API for brand-name resolution and concept identifier assignment
- A two-pass approach uses NER as the primary extractor with RxNorm approximate search as a fallback

## Interaction Checking

- Pairwise drug-drug interactions are looked up bidirectionally against a pre-built DrugBank SQLite database containing approximately 19,800 drugs
- Lookups run in parallel for both A-to-B and B-to-A directions
- An in-process cache with a 24-hour TTL reduces repeated database queries
- The DrugBank database is accessed via a Model Context Protocol server running as a sidecar Node.js process

## Severity Classification

- A zero-shot classification model assigns severity labels to detected interactions
- A regex keyword matcher provides fallback severity classification when the model is inconclusive

## Health Checks

- Liveness and readiness probes verify service availability and DrugBank connection status

## Constraints

- Explicitly informational and self-educational only; not a medical device and provides no medical-advice guarantee
- Interaction data is limited to the vendored DrugBank SQLite snapshot; no live DrugBank API calls
- Severity classification is automated and not clinically validated
- Only pairwise interaction checks are documented; no multi-drug combinatorial interaction matrix
- No authentication, rate limiting, persistent storage, or audit logging
- The single container image bundles both Python and Node.js runtimes
