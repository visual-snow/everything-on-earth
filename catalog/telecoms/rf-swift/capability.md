RF Swift is a containerized wireless security toolkit that turns any Linux or macOS machine into a full RF assessment lab. It ships over 15 specialized images covering SDR analysis, mobile network simulation (2G through 5G), Bluetooth, Wi-Fi, RFID, automotive, hardware hacking, and binary reversing. A unified CLI manages the full container lifecycle — launching, upgrading, profiling, and cleaning up environments without manual container commands.

## SDR and Spectrum Analysis
- Broad SDR hardware support: USRP, RTL-SDR, HackRF, BladeRF, Airspy, LimeSDR, PlutoSDR, and others via SoapySDR
- Spectrum visualization and signal analysis with GNU Radio, GQRX, SDR++, SDRangel, SigDigger, and CyberEther
- Signal demodulation and protocol reverse engineering via Universal Radio Hacker and Inspectrum
- Satellite and GNSS reception with GNSS-SDR and SatDump; ADS-B decoding with dump1090
- LoRa, drone Remote ID, and HF/VHF data link decoding via GNU Radio OOT modules
- GPU-accelerated signal processing with OpenCL on Intel and NVIDIA hardware
- Interactive RF analysis via Jupyter notebook environment

## Telecom (2G–5G)
- 2G/3G base station simulation with YateBTS, OpenBTS, and OsmoCom BTS Suite
- 4G LTE and 5G NR lab stacks built on srsRAN, Open5GS, UERANSIM, and PyHSS
- Protocol-level analysis and attack tooling for SS7, Diameter, GTP via SigPloit, jSS7, and SCAT
- SIM card and protocol introspection with PySIM and pycrate; 5G traffic replay via 5Greplay

## Wireless Protocols
- Bluetooth Classic and BLE assessment: BlueZ, WHAD, Mirage, Sniffle, ice9-bluetooth
- Wi-Fi 802.11 a/b/g/n/ac/ax including WPA3 attack tools: Aircrack-ng, EAPHammer, Dragonslayer, Wifiphisher, Hostapd-mana
- RFID and NFC: Proxmark3 (RRG/Iceman firmware), libnfc, mfoc, mfcuk, miLazyCracker
- Automotive: CAN bus tooling (can-utils, Caring Caribou, SavvyCAN, Gallia) and V2G protocol injection

## Hardware and Reversing
- Logic analysis with PulseView, DSView, and Saleae Logic 2
- Firmware flashing and FPGA programming: Flashrom, OpenOCD, esptool, openFPGALoader
- Binary analysis and disassembly: Ghidra, Radare2, Cutter, ImHex, Binwalk
- Coverage-guided fuzzing with AFL and Honggfuzz; static analysis with Semgrep and Joern

## Network and Operational
- Network reconnaissance and exploitation: Nmap, Metasploit, Burp Suite, Impacket, NetExec, Responder
- Wireless traffic capture: Wireshark, Kismet, Bettercap
- Declarative YAML recipe engine for composing and reproducing custom image builds
- Session recording mode for audit and documentation; rootless Podman mode for hardened environments

## Constraints
- USB SDR hardware passthrough on macOS requires a Lima/QEMU virtual machine layer; native Docker Desktop on macOS cannot forward USB devices
- Direct SDR hardware access inside containers requires privileged mode or explicit device and cgroup rules; rootless Podman may need additional kernel configuration
- Desktop GUI mode is only available in images that ship a VNC server; not all images include it by default
- GPU OpenCL acceleration is restricted to dedicated GPU-variant images and requires host OpenCL drivers accessible from within the container
- Windows and macOS hosts cannot use host network mode; tools requiring monitor-mode Wi-Fi or raw network access need a Linux host or Lima VM
- The image dependency hierarchy is fixed; custom recipe builds must follow the required base-image chain or they will fail
