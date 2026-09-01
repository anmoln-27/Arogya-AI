# 📂 Edge Impulse — On-Device Inference Libraries

This directory contains the **Edge Impulse C++ inference libraries** for running Arogya AI ML models directly on microcontrollers.

## Libraries

### Arogya AI_Inference (v1.0)

| Property | Value |
|:---------|:------|
| **Version** | 1.0.0 |
| **Platform** | Edge Impulse Studio Project [#951794](https://studio.edgeimpulse.com/studio/951794) |
| **Architecture** | Universal (`architectures=*`) |
| **Category** | Machine Learning |

The original inference library containing the Edge Impulse SDK and trained model for basic thermal classification.

### Arogya AI_2.0_inferencing (v2.0)

| Property | Value |
|:---------|:------|
| **Version** | 1.0.1 |
| **Platforms** | ESP32, Arduino Nano 33 BLE Sense (Rev1 & Rev2), Portenta H7, Nicla Vision, Nicla Sense, RP2040, Sony Spresense |
| **Dependencies** | `Arduino_LSM9DS1`, `PDM`, `Arduino_OV767X` |
| **Category** | Data Processing |

Enhanced inference library with support for **9 different MCU platforms** and multimodal sensor input.

## Supported Boards (v2.0)

| Board | Directory |
|:------|:----------|
| ESP32 | `examples/esp32/` |
| Arduino Nano 33 BLE Sense | `examples/nano_ble33_sense/` |
| Arduino Nano 33 BLE Sense Rev2 | `examples/nano_ble33_sense_rev2/` |
| Arduino Nicla Sense | `examples/nicla_sense/` |
| Arduino Nicla Vision | `examples/nicla_vision/` |
| Arduino Portenta H7 | `examples/portenta_h7/` |
| Raspberry Pi RP2040 | `examples/rp2040/` |
| Sony Spresense | `examples/sony_spresense/` |
| Static Buffer (Generic) | `examples/static_buffer/` |

## Getting Started

1. Copy the desired library folder to your Arduino `libraries/` directory
2. Open Arduino IDE and select your target board
3. Open the example sketch for your board from `File → Examples`
4. Upload to your device

## Documentation

- [Deploy as C++ Library](https://docs.edgeimpulse.com/docs/deploy-your-model-as-a-c-library)
- [Running Your Impulse Locally](https://docs.edgeimpulse.com/docs/running-your-impulse-locally-1)
- [C++ SDK API Reference](https://docs.edgeimpulse.com/reference/inferencing-sdk)
