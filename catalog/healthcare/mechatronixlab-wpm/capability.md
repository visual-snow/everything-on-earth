# WPM Capabilities

WPM (Wearable Patient Monitor) is a proof-of-concept hardware prototype running on an STM32WL55JC1 microcontroller. It measures SpO2, heart rate, perfusion index, and finger temperature via a MAX30102 pulse oximetry sensor, tracks motion via a 6-axis IMU, and transmits data over LoRa at 915 MHz to a separate receiver module. It is not a certified medical device.

## Vital Signs

- Peripheral oxygen saturation (SpO2) computed via ratio-of-ratios linear regression on red and infrared LED signals
- Heart rate derived from derivative peak detection on the red LED channel
- Perfusion index calculated from the AC/DC ratio of pulse oximetry signals
- Finger temperature read from the MAX30102 internal temperature sensor

## Motion Tracking

- Three-axis accelerometer and three-axis gyroscope data from a 6-axis IMU sampled at 30 Hz

## Communication

- Sensor data is transmitted at 1 Hz over LoRa at 915 MHz with 500 kHz bandwidth and spreading factor 11
- A separate receiver module built from a Blue Pill board and SX1276 LoRa module receives the transmissions
- A serial debug mode streams raw sensor data at 30 Hz over USB UART

## Display and Alerts

- A monochrome OLED display shows current vital sign readings
- A piezoelectric buzzer provides audible alerts via PWM tone generation

## Constraints

- Not a certified medical device; not tested for electrical safety, EMC, or clinical accuracy
- SpO2 algorithm uses simplified linear regression introducing deviation from clinical-grade values
- The LoRa receiver requires a separate Blue Pill and SX1276 module assembled independently
- No battery or power management circuit; the prototype operates from mains/USB power only
- No LoRaWAN stack; raw LoRa point-to-point only with no cloud or IoT platform integration
- No RTOS or task scheduler; bare-metal firmware architecture
- ECG, blood pressure, and respiration rate are listed as goals but not implemented
