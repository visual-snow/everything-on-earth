# CDC DEX FHIR Tools Capabilities

CDC DEX FHIR Tools is a collection of experimental utilities from the CDC Data Exchange program for working with HL7 FHIR servers. It covers SMART authentication client implementation, JWKS key management, Implementation Guide resource loading, and IG directory filtering. All tools are explicitly non-production and include no hardening or secret management.

## SMART Authentication Client

- Implements SMART App Launch client authentication in both symmetric (shared secret) and asymmetric (private key JWT) modes
- Supports RS256 and RS384 signing algorithms for asymmetric authentication
- Provides a runtime configuration store that can be updated via HTTP POST

## Key Management

- Generates RSA JWKS key pairs for asymmetric SMART authentication
- A serverless function exposes the public portion of generated JWKS over HTTP for FHIR server verification

## Implementation Guide Loading

- Bulk-loads IG resource JSON files into a FHIR server via authenticated HTTP PUT
- Processes flat directories of resource files; subdirectory traversal is not supported
- Falls back to unauthenticated loading if the token acquisition fails

## IG Resource Filtering

- A compiled utility filters downloaded IG directories to retain only CapabilityStatement, StructureDefinition, ValueSet, and CodeSystem files
- Skips example, OpenAPI, and XML directories during filtering

## Connectathon Demos

- Includes synthetic HL7 v2 ELR messages and API collection files for HL7 FHIR Connectathon workflows

## Constraints

- Explicitly non-production; no hardening, rate limiting, or production secret management
- Key rotation for the JWKS function requires redeployment; no dynamic key refresh
- IG filter rules are hard-coded in source; no runtime configuration
- IG loader processes only flat directories; no recursive subdirectory support
- No automated tests; all test scripts in package definitions are no-ops
- No Docker, CI/CD pipeline, or FHIR resource validation before loading
