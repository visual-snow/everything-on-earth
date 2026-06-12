# Gadgetbridge Capabilities

Gadgetbridge is an Android companion app for Bluetooth wearables, trackers, headphones, and health devices. It operates entirely on-device; no vendor accounts, cloud services, or external servers are involved at any point. All health and activity data is stored locally.

Two operational modes:
- Normal mode: a persistent background service maintains device connections and syncs data automatically.
- Debug mode: verbose logging and raw packet inspection are available for protocol diagnostics.

## Connectivity

- Communicates with devices over Bluetooth Low Energy and Bluetooth Classic.
- Supports a wide range of vendors and device families, including Pebble, Xiaomi/Huami, Garmin, Huawei/Honor, Fossil, Sony, and Bangle.js; community-contributed protocol implementations vary in completeness per model.
- Forwards Android notifications to connected devices with per-device filtering rules.
- Exposes an intent-based API for integration with third-party automation apps.

## Measurement

- Step count, distance, active and total calories, and VO2 Max.
- Heart rate: continuous, resting, and recovery; heart rate variability (HRV).
- Blood oxygen saturation (SpO2) and respiratory rate.
- Sleep staging: light, deep, REM, and restless moments.
- Stress and body energy score.
- ECG raw data (device-dependent).
- Blood pressure and blood glucose (meter-dependent).
- Body weight (connected scales).
- GPS tracks for outdoor workouts.
- Body and environmental temperature (device-dependent).

## Configuration

- Notification forwarding rules are configured per connected device.
- Alarm management is handled through the app.
- Weather provider and calendar sync with event filtering are selectable.
- Heart rate monitoring interval is configurable.
- Measurement units toggle between metric and imperial.
- Reconnect timeout and retry behavior are adjustable.
- Data export to Android Health Connect can be toggled per metric type.

## Data Management

- All data is stored in a local SQLite database; nothing leaves the device unless the user explicitly exports it.
- The database can be backed up and restored via ZIP export and import.
- Health metrics are displayed in an on-device dashboard with charting.
- Data can be forwarded to Android Health Connect for aggregation with other health apps.

## Constraints

- Android-only; no iOS, desktop, or server component exists.
- Requires Android 5.0 or higher.
- No cloud backend, web interface, or REST API for remote data access.
- No multi-user or remote-monitoring architecture; one phone, one database.
- Vendor firmware updates may break existing protocol support.
- No built-in ECG interpretation or medical analysis; raw data only.
