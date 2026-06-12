# OntoBrowser Capabilities

OntoBrowser is a Java EE web application for collaborative curation and management of ontologies and controlled terminologies. It enables expert curators to map code list terms from multiple source systems to preferred ontology terms through a peer review and approval workflow. Originally developed under the EU eTOX consortium and published in Bioinformatics (2017).

## Ontology Management

- Interactive web interface for browsing, editing, and curating ontology terms and hierarchies
- Peer review and approval workflow governs all curation actions with a full audit trail
- Automated synonym matching suggests fuzzy-matched terms for curator review
- Hierarchical and graph visualizations of term relationships are rendered via an external graph layout engine

## Search

- Full-text cross-ontology search via an embedded text index enables rapid term discovery across all loaded terminologies

## Import and Export

- Ontologies can be ingested via REST API in OBO format 1.2
- Export supports OWL (RDF/XML, OWL/XML, Manchester Syntax, Turtle), OBO, and JSON formats
- Batch ETL loading of controlled vocabulary terms is supported via direct database insertion

## Integration

- An HTTP reverse proxy with external authentication (Basic Auth or corporate SSO) handles access control
- Email notifications are sent for curation workflow events via an SMTP mail subsystem

## Constraints

- REST import accepts OBO format 1.2 only; OWL and other formats cannot be ingested via the API
- Production deployments are validated on Oracle only; MySQL and PostgreSQL require source code modifications before building
- The graph layout engine must be installed on the server; concurrent process pooling must be configured to prevent resource exhaustion
- Authentication is fully external; the application has no built-in user login or management interface
- No Docker, SPARQL endpoint, OWL import via API, SKOS support, or FHIR terminology format support
