# 📂 Firmware — ESP32 Firmware & Flashing

This directory contains the **firmware files** for the Arogya AI edge device, targeting the **ESP32-S3** microcontroller.

## Overview

The firmware handles:
- Sensor initialization and data acquisition
- Serial data output (for `asha_logger.py` collection)
- On-device inference using the Edge Impulse SDK
- OLED display output and LED triage indicators

## Hardware Target

| Property | Value |
|:---------|:------|
| **MCU** | ESP32-S3 (Dual-core 240 MHz, 512 KB SRAM) |
| **Flash** | 4 MB (minimum) |
| **Framework** | Arduino / ESP-IDF |
| **IDE** | Arduino IDE 2.0+ or PlatformIO |

## Flashing Instructions

### Using Arduino IDE

1. Install **ESP32 Board Support** in Arduino IDE:
   - File → Preferences → Add Board URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
2. Select board: **ESP32S3 Dev Module**
3. Install required libraries from `edge-impulse/`
4. Open the firmware `.ino` file
5. Connect ESP32 via USB and select the correct COM port
6. Click **Upload**

## Pin Configuration

| Sensor | ESP32-S3 Pin | Protocol |
|:-------|:-------------|:---------|
| MLX90640 | SDA=GPIO21, SCL=GPIO22 | I²C |
| MAX30102 | SDA=GPIO21, SCL=GPIO22 | I²C (shared bus) |
| MPU6050 | SDA=GPIO21, SCL=GPIO22 | I²C (shared bus) |
| MQ135 | GPIO34 | Analog |
| GSR | GPIO35 | Analog |
| OLED SSD1306 | SDA=GPIO21, SCL=GPIO22 | I²C (shared bus) |
| LED (Green) | GPIO25 | Digital |
| LED (Yellow) | GPIO26 | Digital |
| LED (Red) | GPIO27 | Digital |

> **Note**: Pin assignments may vary based on your specific wiring. Update accordingly in the firmware source.
