# MedEdge-Gateway Capabilities

MedEdge-Gateway is a demonstration three-tier medical device IoT platform that translates Modbus TCP device telemetry through MQTT to FHIR R4 Observations, with real-time SignalR dashboards and ML-based anomaly detection. Built on ASP.NET Core and .NET 8. This is a portfolio project only; it is not intended for clinical use and processes no real patient data.

## Device Integration

- Modbus TCP simulators emulate infusion pumps, dialysis machines, and filtration devices
- An MQTT broker collects device telemetry from Modbus-connected simulators
- A transform service converts MQTT payloads to FHIR R4 Observation resources with LOINC code mapping

## FHIR API

- Exposes FHIR R4 Patient, Device, and Observation resources over a REST endpoint
- Built on the Firely .NET SDK for FHIR resource handling

## Anomaly Detection

- An AI clinical engine using ML.NET and ONNX Runtime detects anomalous vital sign patterns in real-time telemetry streams

## Dashboards and Analytics

- A SignalR-based real-time dashboard displays device status and clinical alerts
- Analytics endpoints provide summary statistics, trend analysis, station performance, and area comparisons

## Three-Tier Architecture

- Local tier stores full PHI with seven-year retention in a local database
- Regional tier stores anonymized data in a clustered database with ten-year retention
- Global tier stores only device metadata with twenty-five-year retention and zero PHI

## Constraints

- Demonstration project only; NOT for clinical use or production deployment with real patient data
- No actual HIPAA, GDPR, FDA 21 CFR Part 11, or ISO 13485 certification; compliance patterns are demonstrated only
- Azure IoT Hub configured on the Free tier; limited scale for real workloads
- Data anonymization at the regional tier is not cryptographic
- ML anomaly detection models are demonstration-grade with no explainability support
- No multi-tenancy isolation enforcement or audit logging dashboard
