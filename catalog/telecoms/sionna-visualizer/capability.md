Sionna Visualizer is a full-stack web dashboard that wraps NVIDIA's open-source 6G simulation library in a browser interface, turning raw simulation output into interactive, publication-ready charts. It supports AWGN BER, beam pattern, path loss, channel capacity, and modulation comparison simulations without requiring users to write code. Authentication is handled via JWT, and results can be shared publicly via per-simulation links or consumed programmatically through a REST API with API keys.

## Simulation Types

- BER vs SNR curves for BPSK, QPSK, 16QAM, and 64QAM — both theoretical and Monte Carlo
- Beam pattern polar charts for ULA antennas at configurable element counts and frequency bands (28, 39, 60, 77 GHz)
- Path loss per-ray free-space path loss displayed as bar, scatter, and delay charts with a data table
- Channel capacity computed via the Shannon theorem with four bandwidth curves

## Configuration

- Modulation type selectable: QPSK, BPSK, 16QAM, 64QAM
- SNR range controlled via minimum, maximum, and step count parameters
- Antenna element count: 8, 16, 32, or 64
- Frequency band: 28, 39, 60, or 77 GHz
- Seven colormap palettes including colorblind-safe and publication options

## Observability and Fault Tolerance

- Simulation performance metadata captured: duration, memory usage, CPU/GPU utilization, library version
- Complexity estimate (Fast / Medium / Slow / Heavy) displayed before execution begins
- Circuit breaker on the Python bridge — backend handles bridge failures gracefully and reports bridge status
- Rate limiting of 10 simulations per minute per IP protects the simulation layer from overload
- Health endpoint exposes a warm/cold indicator for the Python bridge

## Deployment Modes

- All-local mode: all four services started together from a single compose file
- Manual mode: each service started independently in separate terminals
- Cloud/production mode: backend and Python bridge on Railway, frontend on Vercel, with GitHub Actions auto-deploy
- Authenticated mode: JWT login required for simulation history, API key management, and bulk export
- Public mode: shareable links per simulation require no login; REST API accessible with a pre-issued API key

## Constraints

- The NVIDIA Sionna SDK must be installed in the Python bridge environment; GPU acceleration is optional but the underlying TensorFlow dependencies significantly increase image size and startup time
- The public REST API is rate-limited to 100 requests per day per API key; the simulation endpoint requires a pre-issued key from the dashboard
- Simulation caching is in-memory and non-persistent — the cache is lost on backend restart, causing identical parameters to incur full re-computation
- All four services depend on database credentials supplied via environment variables before startup; missing credentials will prevent the database service from initializing
- Simulations are synchronous HTTP calls with no streaming or progress feedback — the client blocks until the full response is returned
