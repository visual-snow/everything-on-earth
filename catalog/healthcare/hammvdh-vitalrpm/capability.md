# VitalRPM Capabilities

VitalRPM is a Flutter-based remote patient monitoring application that tracks six vital signs and uses machine learning to classify patient health status and forecast future vital sign values. Built as an academic project using MIMIC-III triage data; the backend is a Flask API. No real-time sensor or wearable device integration is included; vitals must be entered manually or sent via API.

## Vital Signs Monitoring

- Tracks temperature, heart rate, respiratory rate, oxygen saturation (SpO2), systolic blood pressure, and diastolic blood pressure
- Patient data and assets are stored in a cloud database with real-time synchronization to the mobile client

## Health Status Classification

- A hybrid machine learning model classifies patient health into a five-level acuity scale from critical to normal
- The model was trained on a 10% sample of MIMIC-III triage records with SMOTEENN resampling to address class imbalance

## Vital Sign Forecasting

- An XGBoost time-series model predicts future vital sign values from current measurements
- The forecasting model was built from a single MIMIC-III patient trajectory; generalization to other patients is not validated

## API

- A forecast endpoint accepts current vitals and returns predicted future values with derived health status
- A status endpoint accepts current vitals and returns health status classification only

## Constraints

- Health status is a five-class acuity label only; no continuous risk score is produced
- The forecasting model was trained on a single patient trajectory and has not been validated for generalization
- No authentication or rate limiting on the API endpoints
- No real-time sensor, wearable, or device integration; vitals must be submitted via API call
- No HL7, FHIR, or EHR interoperability
- No Docker deployment; uses a platform-as-a-service deployment with debug mode enabled in production
