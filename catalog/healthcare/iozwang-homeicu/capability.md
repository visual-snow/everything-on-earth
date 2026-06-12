# HomeICU Capabilities

HomeICU is an open-source low-cost remote vital signs monitor built on ESP32 hardware. It pairs a wearable wireless sensor tag with a Flutter mobile app (MyChart) to let clinicians track home patients recovering from illness. The project is a pre-release prototype; it is not approved for use on human subjects and is restricted to laboratory evaluation by qualified engineers.

## Vital Signs Monitoring

- Body temperature measurement via a precision temperature sensor
- Peripheral oxygen saturation (SpO2) via pulse oximetry
- Heart rate and heart rate variability from the pulse oximetry waveform
- Single-lead ECG via an analog front-end with impedance pneumography for respiration rate
- Motion detection and cough intensity via a three-axis accelerometer

## Connectivity

- The sensor tag communicates with the MyChart mobile app over Bluetooth Low Energy
- In base-station mode, the app relays vital signs data to a cloud server
- A planned standalone mode uses MQTT for direct cloud upload without a smartphone intermediary
- The ESP32 provides Wi-Fi for network backhaul

## Mobile Application

- The MyChart Flutter app runs on iOS and Android
- Displays real-time vital signs from the paired sensor tag
- Configurable alert thresholds per vital sign for clinician notifications

## Hardware

- Built on ESP32 WROOM32 with dedicated analog front-ends for ECG, pulse oximetry, and temperature
- Powered by a rechargeable LiPo battery with USB on-board charging
- PCB schematics and board files are published for reproducibility

## Constraints

- Pre-release prototype; firmware and hardware are draft versions with no formal release
- Not certified by any regulatory authority (FDA, CE, Health Canada); not approved for human use
- Restricted to laboratory electrical evaluation with isolated power supply
- No blood pressure monitoring in the current hardware; planned for a future phase
- No wearable enclosure design, GPS module, or server-side backend code in the current repository
- No automated test suite or CI pipeline
