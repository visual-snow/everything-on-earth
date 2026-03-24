This sandbox provides a fully emulated 5G network that integrates Non-Terrestrial Networks (NTN) as backhaul links, enabling comparative evaluation of slice-aware versus slice-unaware satellite routing. The architecture is 3GPP Release 17 compliant and comprises a complete 5G core (free5GC), a simulated RAN with one gNB and nine UEs (UERANSIM), and emulated GEO and LEO satellite trunks. Tasks can drive the testbed through complete experimental iterations and analyze per-slice QoS outcomes.

## 5G Core Control Plane
- Full set of 3GPP core network functions: AMF, SMF, PCF, NRF, NSSF, UDM, UDR, AUSF
- NTN-enabled SMF with a custom QoS function (NTNQOF) for satellite-aware session management
- Network slice selection driven by S-NSSAI with per-slice UPF instantiation (three slices)
- PDU Session establishment over N2, N3, and N4 reference interfaces

## Non-Terrestrial Network Emulation
- Two satellite backhaul links: GEO trunk (high latency) and LEO trunk (lower latency)
- Configurable NTN link parameters: bandwidth, propagation delay, and ACM simulation
- Slice Classifiers at both the RAN-NTN and NTN-CN boundaries for traffic steering
- Slice-aware mode routes each slice to the appropriate satellite link based on QoS requirements
- Slice-unaware mode provides a baseline with undifferentiated routing across links

## Radio Access and User Equipment
- One gNB simulated via UERANSIM running 5G NR
- Nine UE instances, each capable of independent PDU Session attachment per slice
- Try-retry fault injection: iterations with any UE stuck in IDLE state are aborted and restarted

## Measurement and Analysis
- Per-slice throughput and latency metrics collected for each experimental iteration
- Full PCAP capture of all network traffic generated per iteration
- Probe files written per iteration for post-hoc analysis
- Matplotlib-based result visualization with LaTeX/TikZ export support
- Configurable iteration count for statistical repeatability

## Configuration Surface
- Global testbed settings: satellite image selection, service configurations, output targets
- Slice-to-satellite-link assignment with timing windows
- Application instantiation per slice, UE count, and total scenario duration

## Constraints
- Requires a minimum of 8 CPU cores, 8 GB RAM, and 50 GB disk storage to run the full scenario
- Each experimental iteration generates approximately 13 GB of PCAP capture data, requiring substantial available storage
- The full scenario runs approximately 240 seconds per iteration; multi-iteration runs multiply wall-clock time accordingly
- Host kernel must support the GTP module required by free5GC; standard Linux kernels without this module are incompatible
- No UE mobility or satellite handover is modeled; all UEs remain stationary throughout the scenario
- No security or encryption plane is exercised; authentication mechanisms are present but not under test
