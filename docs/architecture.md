# 🏗️ Arogya AI System Architecture

## Overview

Arogya AI is a **multi-layer edge-AI system** that processes sensor data locally on an ESP32-S3 microcontroller. The architecture is designed for:

- **Zero-latency inference** (no cloud dependency)
- **Multi-sensor fusion** (thermal + spectral + physiological)
- **Low power consumption** (battery-powered field operation)
- **Modular design** (sensors can be added/removed independently)

---

## System Layers

### Layer 1: Sensor Array

| Sensor | Data Type | Sampling Rate | Output |
|:-------|:----------|:-------------|:-------|
| MLX90640 | 24×32 thermal frame | 2 Hz | Temperature matrix (°C) |
| MAX30102 | PPG waveform | 100 Hz | SpO₂ (%), Heart Rate (BPM) |
| MQ135 | Analog voltage | 10 Hz | Gas concentration (ppm) |
| GSR | Analog voltage | 10 Hz | Skin conductance (µS) |
| AS7341 | 11-channel spectral | 1 Hz | Light intensity per wavelength |
| MPU6050 | 6-axis IMU | 50 Hz | Acceleration (g), Gyro (°/s) |

### Layer 2: Signal Preprocessing (ESP32-S3)

- **Thermal**: Frame normalization, ROI extraction (forehead region)
- **PPG**: Band-pass filtering, peak detection, SpO₂ calculation
- **Gas**: Baseline subtraction, threshold detection
- **GSR**: Smoothing, stress index calculation
- **Spectral**: Multi-channel ratio analysis for hemoglobin estimation
- **IMU**: Motion artifact rejection, activity classification

### Layer 3: AI Inference

```
Thermal Frame (24×32) → FeverCNN (ONNX/TFLite) → Fever Score
PPG Signal → Signal Processing → SpO₂ + Heart Rate
Spectral Data → Hemoglobin Model → Anemia Risk Score
GSR + HRV → Stress Model → Stress Level
Gas + Respiratory → Pattern Analysis → Respiratory Score
```

### Layer 4: Multi-modal Fusion & Triage

All individual scores are combined into a **Health Triage Index**:

| Triage Level | LED Color | Action |
|:-------------|:----------|:-------|
| 🟢 **Normal** | Green | Continue monitoring |
| 🟡 **Caution** | Yellow | Re-test / closer observation |
| 🔴 **Alert** | Red | Immediate referral to PHC |

---

## Data Flow Diagram

```
ESP32-S3
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Sensors ──► Preprocessing ──► Feature Extraction    │
│                                       │              │
│                                       ▼              │
│                              ┌─────────────────┐    │
│                              │ TFLite Runtime   │    │
│                              │ (FeverCNN ~119KB)│    │
│                              └────────┬────────┘    │
│                                       │              │
│                                       ▼              │
│                              Fusion & Triage         │
│                                       │              │
│                              ┌────────┼────────┐    │
│                              ▼        ▼        ▼    │
│                            OLED    LEDs    Serial    │
│                           Display  🟢🟡🔴  Logger    │
└──────────────────────────────────────────────────────┘
```

---

## Model Deployment Pipeline

```
PyTorch (.py) → Train → .pth → Export → .onnx → Edge Impulse → .tflite → ESP32 Flash
```

1. **Training**: `scripts/train_fever_model.py` trains FeverCNN on labeled thermal data
2. **Export**: `scripts/export_fever_to_onnx.py` converts to ONNX format
3. **Optimization**: `scripts/finalize_onnx.py` applies graph optimizations
4. **Deployment**: Upload to Edge Impulse Studio or directly flash via Arduino IDE

---

## Communication Protocol

```
ESP32 ←─── USB Serial (115200 baud) ───→ PC (asha_logger.py)
  │
  └─── I²C Bus (400 kHz) ───→ MLX90640, MAX30102, MPU6050, AS7341, OLED
  │
  └─── ADC ───→ MQ135 (GPIO34), GSR (GPIO35)
  │
  └─── GPIO ───→ LED Green (25), Yellow (26), Red (27)
```
