Blockstream Satellite is a Python toolkit for receiving a globally broadcast satellite signal that carries the Bitcoin blockchain over DVB-S2. It supports four receiver hardware types and provides a CLI wizard for configuration, a GUI, and a paid API for transmitting arbitrary messages via Lightning Network payments. Bitcoin nodes can sync entirely from satellite without an internet connection or in a hybrid mode alongside one.

## Configuration
- Interactive setup wizard covers satellite selection, receiver type, antenna size, and LNB model
- Five satellites supported: Galaxy 18, Telstar 11N Africa, Telstar 11N Europe, Telstar 18V C-Band, Telstar 18V Ku-Band
- Four receiver types supported: Linux USB, Software-Defined Radio, Standalone IRD, and Sat-IP integrated antenna
- Named configuration sets allow multiple profiles in the same environment

## Receiver Modes
- SDR mode uses an RTL-SDR dongle with software demodulation
- Linux USB mode uses a TBS DVB-S2 USB receiver with kernel drivers
- Standalone mode manages a professional IRD over IP
- Sat-IP mode uses a flat-panel integrated antenna with IP output

## Signal Monitoring
- Per-receiver metrics include carrier lock, signal level, signal-to-noise ratio, bit error rate, frame error rate, and packet error rate
- Signal quality is expressed as a 0-100% value
- Metrics can be reported to a remote TLS-authenticated monitoring endpoint

## API and Messaging
- Satellite API supports four channels: USER (paid), AUTH, GOSSIP (Lightning gossip snapshots), and BTC-SRC (Bitcoin source code)
- Message transmission to USER channel requires a Lightning Network bid in millisatoshis
- Messages can be GPG-encrypted and signed before transmission
- Forward error correction is applied to API messages
- A testnet API server is available for order testing without real payments
- A demo receiver class supports API listener testing without real satellite hardware

## Bitcoin Node Integration
- Satellite-only mode enables full blockchain sync with no internet connection
- Hybrid mode combines internet and satellite sources simultaneously

## Constraints
- Hardware receiver commands (USB, SDR, Standalone, Sat-IP, firewall, and related subcommands) are Linux-only; macOS and Windows support is limited to configuration, instructions, API, and Bitcoin subcommands
- C-band satellites are incompatible with flat-panel and Sat-IP antenna types
- RTL-SDR mode requires kernel-level pipe buffer tuning to function correctly
- USB receivers require out-of-tree TBS kernel drivers installed separately
- GPG keyring must be configured before sending encrypted API messages
- No emulated satellite signal source exists for fully offline end-to-end testing
