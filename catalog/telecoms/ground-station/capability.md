Ground Station is an open-source satellite tracking and radio communication suite built for amateur radio operators and researchers. It combines a web-based frontend with a multi-worker backend to support real-time and automated satellite observation workflows. The system integrates GNU Radio for signal processing and SatDump for METEOR satellite image decoding.

## Satellite Tracking
- Real-time orbital parameter calculation using TLE data
- Automated pass predictions with configurable elevation thresholds and lookahead windows
- TLE synchronization from CelesTrak and SatNOGS databases
- Scheduled observations triggered automatically by pass predictions

## SDR Signal Acquisition
- IQ signal acquisition via the SoapySDR ecosystem, supporting RTL-SDR, Airspy, AirspyHF, HackRF, PlutoSDR, LimeSDR, SDRplay, USRP, HydraSDR, and bladeRF
- USRP hardware support via UHD v4.9.0.0
- Local and remote SDR discovery via mDNS service discovery
- Multiple simultaneous SDR sessions with independent configuration per receiver
- IQ playback through a virtual SDR device

## Signal Processing and Demodulation
- Spectrum analysis and waterfall visualization via FFT processing
- FM, SSB, and AM demodulation
- SSTV image decoding
- METEOR satellite image processing via SatDump integration
- IQ recording with full orbital metadata in SigMF format

## Radio Control
- Hamlib CAT protocol for antenna and radio frequency control
- Simultaneous user-facing demodulation and internal decoder pipeline operation

## Data and Monitoring
- Per-subscriber queue health metrics and data-flow statistics
- Live speech-to-text transcription (Gemini Live or Deepgram)
- Real-time signal streaming to the browser via WebSocket

## Constraints
- AFSK packet, LoRa, and GMSK decoders are marked as work-in-progress and currently non-functional
- NOAA APT weather satellite decoding is not yet implemented
- METEOR image processing depends on the bundled SatDump installation pinned to a specific upstream commit; upgrading SatDump independently may break compatibility
- USB SDR device access and mDNS discovery require the container to run with host networking and elevated privileges
- Persistent storage for the database, recordings, snapshots, and firmware images must be provided via an external volume mount
