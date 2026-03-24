UnifyAir Core is a 3GPP-compliant 5G Core Network implemented in Rust, currently shipping a production Access and Mobility Management Function named Omnipath. The integration environment pairs Omnipath with supporting network functions from the a companion 5G core suite and a gNB/UE simulator for end-to-end test execution. Structured logging and packet capture tooling provide full observability into both control-plane and user-plane traffic.

## Access and Mobility Management

- Handles UE registration, authentication, and security mode procedures over the NAS layer
- Connects to gNB over the N2 interface using SCTP transport
- Exposes a Service-Based Interface for NF-to-NF REST communication, supporting Namf-comm, Namf-evts, Namf-mt, and Namf-loc services (TS 29.518)
- Configurable PLMN, GUAMI, TAI, S-NSSAI, NAS security algorithms, and NAS timer values

## Integration Testing

- Full 5G Core stack is exercisable end-to-end using a gNB simulator with configurable UE profiles (registration, PDU session establishment, and error paths)
- A packet-capture sidecar records all network traffic during test runs for post-hoc analysis
- An HTTP/2 decoder can decode SBI traffic from captured packet files
- Subscriber data is seeded automatically into a document database via a dedicated initialization container

## Observability

- Structured logging with five severity levels (trace, debug, info, warn, error) emitted by Omnipath
- Full panic backtraces available via environment variable flags in debug builds
- Per-profile pass/fail reporting from the gNB simulator after each test run
- Captured packets available as output artifacts for offline protocol inspection

## Constraints

- Only the AMF (Omnipath) is a UnifyAir implementation; SMF and UPF Rust implementations are planned but not present in this repository
- All other 5GC network functions (NRF, AUSF, NSSF, PCF, SMF, UDM, UDR, CHF, NEF) are provided by a companion 5G core images, not UnifyAir implementations
- The user-plane function requires the a GTP kernel module kernel module to be loaded on the host, which may not be available in all sandbox environments
- No TLS is configured between network functions in the default integration setup; all SBI traffic is unencrypted
- No Kubernetes or Helm deployment artifacts are present; cloud-native deployment is a planned feature only
- No dedicated fault-injection, chaos-engineering, or performance benchmarking tooling exists in the repository
