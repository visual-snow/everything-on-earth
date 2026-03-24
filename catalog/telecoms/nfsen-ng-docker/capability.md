This sandbox provides a NetFlow and sFlow collection and visualization environment built on nfsen-ng, a PHP/Apache web UI backed by RRDtool for time-series storage. It supports multiple concurrent flow sources, each assigned a dedicated UDP capture daemon, and exposes a browser-accessible interface for querying and graphing network flow data. The environment handles NetFlow v5/v9, IPFIX, and sFlow traffic simultaneously with automatic recovery if a collector process fails.

## Flow Collection

- Accepts NetFlow v5/v9 and IPFIX traffic via dedicated per-source capture daemons
- Accepts sFlow traffic via a separate sFlow collector daemon
- Supports multiple concurrent flow sources defined in a CSV configuration file
- Each source is assigned a unique UDP port within a fixed range at startup
- A watchdog loop restarts failed collector processes automatically every 60 seconds

## Visualization and Querying

- Graphs view displays RRD time-series per source, protocol, or port
- Flows view provides a paginated table of raw flow records via nfdump queries
- Statistics view shows aggregated metrics orderable by bytes, packets, or flows
- Default protocol breakdown tracks traffic on HTTP, SSH, DNS, and HTTPS ports
- Frontend auto-refreshes every 60 seconds

## Configuration

- Flow sources are defined in a plain-text CSV file specifying device name, port, and protocol type
- Source configuration is parsed at container startup and applied to the web UI automatically
- Adding or removing sources requires a full stack restart; no rebuild is needed
- Per-source RRD databases and captured flow files are stored on a shared persistent volume

## Constraints

- Flow source ports must be unique and fall within the designated UDP port range; sources outside this range are not reachable without reconfiguring the compose stack
- Only one nfdump query process runs at a time — concurrent flow queries are serialized
- Source list changes take effect only after a full stack restart, not via live reload
- The web interface has no authentication or TLS — all access is over plain HTTP
