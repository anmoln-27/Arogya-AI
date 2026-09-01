# 📂 Data — Raw Sensor Logs

This directory contains **raw sensor data** collected from the Arogya AI hardware platform via serial communication.

## Files

| File | Sensor Source | Description | Columns |
|:-----|:-------------|:------------|:--------|
| `environment_smoke_active.csv` | MQ135 + All | Environmental readings during active smoke/gas exposure | Timestamp, ECG, GSR, Gas, Pulse_IR, Temp_Max, Label |
| `representative_thermal_data.npy` | MLX90640 | NumPy array of 24×32 thermal frames for model calibration | (N, 24, 32) float32 |
| `respiration_dataset.csv` | MQ135 + PPG | Breathing pattern data for respiratory analysis | Timestamp, Gas, Pulse_IR, Breathing_Rate, Label |
| `resting_baseline.csv` | All sensors | Baseline readings at rest (control data) | Timestamp, ECG, GSR, Gas, Pulse_IR, Temp_Max, Label |
| `stationary_noise_fidgeting.csv` | IMU + GSR | Motion/fidgeting noise characterization | Timestamp, AccX, AccY, AccZ, GSR, Label |
| `stress_dataset.csv` | GSR + PPG | Galvanic skin response under stress conditions | Timestamp, GSR, Pulse_IR, HRV, Label |

## Collection Method

Data is collected via `utils/asha_logger.py` which reads serial output from ESP32 at **115200 baud** on COM3.

```bash
python utils/asha_logger.py
```

## Notes

- All CSV files use **comma-separated** format with headers
- Timestamps are relative (milliseconds since boot)
- Labels are binary: `0` = Normal/Healthy, `1` = Abnormal/Positive
