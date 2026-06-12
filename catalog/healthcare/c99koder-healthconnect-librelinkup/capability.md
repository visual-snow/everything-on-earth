# HealthConnect-LibreLinkUp Capabilities

HealthConnect-LibreLinkUp is an Android app that syncs Freestyle Libre continuous glucose monitor readings from the LibreLinkUp cloud service into Google HealthConnect and WearOS. It polls the cloud API every 15 minutes and writes new glucose values locally. It does not communicate directly with the sensor via Bluetooth; all data flows through the LibreLinkUp cloud relay.

## Glucose Sync

- Fetches the latest blood glucose reading from the LibreLinkUp cloud API at 15-minute intervals
- Writes glucose values into Google HealthConnect for aggregation with other health apps
- Supports readings in both mg/dL and mmol/L units

## WearOS Integration

- An optional WearOS companion app displays glucose data on the watch
- A WearOS complication shows the current glucose reading on supported watch faces
- A WearOS tile provides a quick-glance glucose summary

## Configuration

- Users select their LibreView region and authenticate with their LibreLinkUp account credentials
- A sharing invitation from the Freestyle Libre app must be accepted before data becomes available

## Constraints

- Requires Android 9.0 or higher on the phone
- Google HealthConnect must be installed (built-in on Android 14+; separate install on earlier versions)
- WearOS 3.0 or later is required for wearable features
- Only Freestyle Libre 2 and Libre 3 sensors linked to a LibreLinkUp account are supported
- No local Bluetooth communication with the sensor; relies entirely on the LibreLinkUp cloud relay
- No historical data backfill; only the latest reading is fetched
- Polling interval is fixed at 15 minutes; not user-configurable
- No iOS or cross-platform support
