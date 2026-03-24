gr-dvbs2rx is a GNU Radio out-of-tree module that provides a complete DVB-S2 transmitter and receiver stack for software-defined radio, implementing physical layer synchronization, LDPC/BCH forward error correction, and MPEG transport stream I/O. It ships three command-line applications — a transmitter, a receiver, and an IQ recorder — that can be piped together for loopback testing without any SDR hardware or connected to real devices for live satellite work.

## Signal Processing

- Full DVB-S2 physical layer: PL frame synchronization, symbol timing recovery, carrier frequency and phase recovery
- SIMD-accelerated LDPC decoder with hardware-accelerated SIMD support; BCH outer FEC
- BBFRAME processing and MPEG transport stream output from the receiver

## Operating Modes

- Loopback via pipe: transmitter stdout fed directly into receiver stdin, no hardware required
- File-based loopback: IQ files used as source or sink for offline testing and playback
- Live SDR reception from RTL-SDR, USRP, bladeRF, or PlutoSDR devices
- Live SDR transmission via USRP, bladeRF, or PlutoSDR
- IQ recording to SigMF-formatted capture files for later offline replay

## Fault Injection

- AWGN noise injection on the transmitter IQ output at a configurable SNR in dB
- Carrier frequency offset injection on the transmitter IQ output in Hz

## Measurement and Monitoring

- Estimated carrier frequency offset, frame lock status, average LDPC iteration count, and SNR reported at runtime
- MPEG transport stream packet counts and bitrate via TSDuck integration
- On-demand JSON metrics available from an HTTP monitoring server
- Periodic console logging of receiver metrics in JSON format

## MPEG TS Integration

- Raw transport stream accepted as transmitter input and produced as receiver output
- UDP/IP over MPEG TS (MPE) supported through TSDuck plugin pipeline
- TS layer processing, demuxing, and analysis delegated entirely to TSDuck

## Constraints

- Only CCM (constant coding and modulation) is supported; ACM and VCM are not implemented
- Only QPSK and 8PSK constellations are supported; 16APSK and 32APSK are absent
- Minimum receivable SNR is approximately 2 dB, and only when pilot symbols are enabled
- RTL-SDR is receive-only; it cannot be used for transmission
- bladeRF and PlutoSDR transmit/receive support is marked experimental
- MPEG TS processing beyond raw stream I/O is out of scope and requires external tooling
- Primarily validated against Blockstream Satellite parameters; other configurations may have reduced test coverage
