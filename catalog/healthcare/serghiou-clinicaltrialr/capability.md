# clinicaltrialr Capabilities

clinicaltrialr is an R package that provides a programmatic interface to the ClinicalTrials.gov legacy API for importing study records as tidy dataframes. It wraps XML parsing and search-result scraping into a small set of R functions suitable for bulk clinical-trial metadata analysis. The package uses the deprecated v1 API which may be retired.

## Data Import

- Downloads and parses all fields of a single study record by NCT identifier
- Scrapes search-result tables from ClinicalTrials.gov Advanced Search URLs
- Returns study metadata as tidy R dataframes for direct use with dplyr and other tidyverse tools

## Bulk Retrieval

- Parallel fetch support enables downloading thousands of study records concurrently using multiple CPU workers
- Progress bars track bulk download completion
- Failed records are identifiable by error strings in the returned list, allowing targeted re-extraction

## Constraints

- Uses the deprecated ClinicalTrials.gov v1 API; the legacy endpoint may be retired without notice and migration to the v2 API is not yet implemented
- No built-in rate-limit back-off or automatic retry logic; throughput is bounded by ClinicalTrials.gov server limits and available CPU cores
- Complex nested fields such as outcomes and interventions are returned as raw list structures, not fully tidied
- Not published on CRAN; installation requires devtools from GitHub
- No bulk XML download path; records must be fetched one at a time
