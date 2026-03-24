Intel FlexRAN is a 4G and 5G baseband PHY reference design that runs on Intel Xeon processors, providing a validated Layer 1 binary implementation for 5G NR signal processing. It ships as pre-compiled binaries tested on SkyLake and CascadeLake platforms and is not available as source code. The sandbox supports downlink-only, uplink-only, and full-duplex test modes against a built-in MAC testing framework.

## Signal Processing

- Implements 5G NR Layer 1 per 3GPP TS 38.211, 38.212, 38.213, 38.214, and 38.215, plus 4G LTE
- Processes PUSCH, PUCCH, PRACH, and SRS channels
- Runs DL, UL, and full-duplex test modes driven by XML multi-slot scenario files
- Compares IQ samples per slot and produces pass/fail validation reports

## Forward Error Correction

- Supports in-CPU FEC via the software FEC SDK integrated with the a hardware abstraction layer data-plane library
- Supports hardware FEC offload to FPGA or ASIC accelerators via the same BBDev interface
- FEC mode is selected at configuration time; only one mode is active per deployment

## Interfaces and Protocols

- Exposes a FAPI v222.10.02 interface layer between Layer 1 and upper-layer software
- Communicates with the MAC testing framework over a proprietary private interface
- Accepts XML configuration files to define multi-slot test scenarios and channel parameters

## Measurement and Validation

- Produces per-slot IQ sample comparison results for downlink, uplink, and full-duplex runs
- Measures real-time latency in microseconds using a latency benchmarking tool on isolated CPU cores
- Validates individual channel types independently or in combined full-duplex mode

## System Configuration

- BIOS settings (CPU power policy, frequency scaling, C-state disabling) are tunable for real-time workloads
- CPU frequency management is applied via processor register inspection tools at the OS level
- Hugepage allocation and CPU isolation are configured through OS kernel parameters and Kubernetes resource manifests

## Constraints

- Requires an Intel Xeon SkyLake or CascadeLake processor; no other CPU families are supported
- Hugepages are mandatory: the L1 application requires 2 GiB and the FAPI layer requires 4 GiB allocated at the host before startup
- Real-time OS tuning — isolated CPUs, disabled C-states, pinned CPU frequency — is required to obtain valid latency measurements
- FEC must run entirely in-CPU or entirely offloaded to FPGA/ASIC; mixed-mode operation is not documented
- Distributed as validated binaries only; rebuild and cross-compilation are not supported
