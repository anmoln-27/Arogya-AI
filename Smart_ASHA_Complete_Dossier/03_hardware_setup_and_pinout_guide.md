# 🔌 Smart-ASHA: Pinout, Wiring & Prototype Setup Guide

**Target Hardware:** 7Semi ESP32-S3 EC200U 4G LTE Smart Modem  
**Reference Document:** `setup.pdf`  
**Revision:** v3.0 — Updated to reflect actual board (7Semi ESP32-S3 + Quectel EC200U)  

---

## 1. System Architecture Diagram

```
              +---------------------------------------------------+
              |  7Semi ESP32-S3 EC200U 4G LTE Smart Modem       |
              |  ┌──────────────┐     ┌──────────────────────┐   |
              |  │  ESP32-S3    │UART │ Quectel EC200U-CN    │   |
              |  │  Dual-Core   │◄───►│ 4G LTE Cat-1         │   |
              |  │  240 MHz     │     │ GPS/GLONASS/BeiDou   │   |
              |  │  WiFi + BLE  │     │ GSM/GPRS Fallback    │   |
              |  └──────┬───────┘     └──────────────────────┘   |
              +---------|-------+-------+-------+---------------+
                        |       |       |       |
       +----------------+       |       |       +----------------+
       |                        |       |                        |
  [Primary I2C: Wire]           |       |           [Secondary I2C: Wire1]
 GPIO 8 (SDA) / GPIO 18 (SCL)  |       |          GPIO 16 (SDA) / GPIO 17 (SCL)
       |                        |       |                        |
       v                        |       |                        v
  +-------------------+         |       |           +-------------------+
  |   TCA9548A Mux    |         |       |           |     MAX30105      |
  |  (Address: 0x70)  |         |       |           |   Pulse / SpO2    |
  +---------+---------+         |       |           +-------------------+
    | | | | |                   |       |
    | | | | +-- Port 7: OLED    |       +-- ADC1 Pin 34: AD8232 (ECG)
    | | | |                     |
    | | | +---- Port 4: AS7343  +----------- ADC1 Pin 35: GSR
    | | |                       |
    | | +------ Port 3: MLX90640+----------- ADC1 Pin 32: MQ-135 (Gas)
    | |
    | +-------- Port 2: MPU6050 IMU
    |
    +---------- Port 0: Reserved (Piezo ADC)
```

---

## 2. Master Pin Connection Matrix

| Subsystem / Sensor | Sensor Pin | ESP32-S3 Pin | Bus / Interface | Notes |
|:---|:---|:---|:---|:---|
| **TCA9548A Multiplexer** | VCC | 3.3V | Power Rail | Main bus multiplexer (Address: `0x70`) |
| | GND | GND | Common Ground | Common system ground |
| | SDA | GPIO 8 | `Wire` (Primary I²C) | Clock speed set to 50 kHz |
| | SCL | GPIO 18 | `Wire` (Primary I²C) | Clock speed set to 50 kHz |
| | RST | 3.3V | Logic High | Pulled high to prevent reset |
| **MAX30105 Pulse/SpO₂** | VCC | 3.3V | Power Rail | Completely isolated from TCA9548A |
| | GND | GND | Common Ground | Common system ground |
| | SDA | GPIO 16 | `Wire1` (Secondary) | Independent bus to prevent contention |
| | SCL | GPIO 17 | `Wire1` (Secondary) | Independent bus to prevent contention |
| **AD8232 ECG Sensor** | 3.3V | 3.3V | Clean Power Rail | Keep away from switching noise |
| | GND | GND | Common Ground | Common system ground |
| | OUTPUT | GPIO 34 | Analog (`ADC1_CH6`) | Safe ADC1 channel (no Wi-Fi/BT conflict) |
| | LO+ | Optional | Digital In | Lead-off detection positive |
| | LO- | Optional | Digital In | Lead-off detection negative |
| **GSR Skin Conductance** | VCC | 3.3V | Power Rail | Voltage divider configuration |
| | GND | GND | Common Ground | Common system ground |
| | SIG / OUT | GPIO 35 | Analog (`ADC1_CH7`) | Safe ADC1 channel |
| **MQ Gas Sensor (MQ-135)** | VCC | 5.0V / VBUS | 5V Rail | Internal heater coil requires 5V |
| | GND | GND | Common Ground | Common system ground |
| | AOUT | GPIO 32 | Analog (`ADC1_CH4`) | Resistive divider to match 3.3V scale |
| **Quectel EC200U-CN** | TX | GPIO (UART TX) | Internal UART | On-board connection to ESP32-S3 (7Semi board) |
| (On-board 4G LTE Modem) | RX | GPIO (UART RX) | Internal UART | On-board connection to ESP32-S3 (7Semi board) |
| | SIM | Micro SIM Slot | On-board | Insert Jio/Airtel/BSNL SIM for 4G data + SMS |
| | GNSS Ant. | u.FL / On-board | On-board | GPS, GLONASS, BeiDou, Galileo |

---

## 3. TCA9548A Multiplexer Channel Map (`Wire`: GPIO 8 / 18)

All devices connected to the multiplexer communicate over the primary I²C bus throttled to **50 kHz**. Only one port is active at any given moment.

| MUX Port | Device Connected | I²C Address | Operational Role | Refresh Strategy |
|:---:|:---|:---:|:---|:---|
| **Port 0** | *Unused* | — | Reserved for acoustic piezo I²C ADC | — |
| **Port 1** | *Unused* | — | Reserved | — |
| **Port 2** | **MPU6050** | `0x68` | 6-Axis Motion, Chest-Wall Tracking | Polled every 1.2 s |
| **Port 3** | **MLX90640** | `0x33` | $24 \times 32$ Far-Infrared Thermal Sensor | Read at 2 Hz frame rate |
| **Port 4** | **AS7343** | `0x39` | 14-Channel Multi-Spectral Optical Sensor | Configured: Gain 128X, 100 ms integration |
| **Port 5** | *Unused* | — | Reserved | — |
| **Port 6** | *Unused* | — | Reserved | — |
| **Port 7** | **SH1106 OLED** | `0x3C` | $128 \times 64$ Monochrome System Display | Updated every 1.2 s – 1.5 s |

---

## 4. Port Switching & Bus Isolation Wrappers

To prevent bus contention and driver lockups on the ESP32-S3, all port switching uses the verified shielding wrappers:

```cpp
// Select a specific port on TCA9548A
void tcaSelect(uint8_t port) {
  if (port > 7) return;
  Wire.beginTransmission(0x70);
  Wire.write(1 << port);
  Wire.endTransmission();
}

// Deselect all ports (Isolates all downstream sub-buses)
void tcaDeselect() {
  Wire.beginTransmission(0x70);
  Wire.write(0x00);
  Wire.endTransmission();
}
```

---

## 5. Arduino IDE Board & Tool Configurations

To prevent stack overflows, memory alignment faults, and partition errors when flashing the full dual-core firmware ([`final_eval.ino`](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Arduino/final_eval/final_eval.ino)), configure the Arduino IDE as follows:

* **Board:** `ESP32S3 Dev Module`
* **USB CDC On Boot:** `Enabled`
* **CPU Frequency:** `240MHz (WiFi)`
* **Core Debug Level:** `None` (or `Verbose` for diagnostics)
* **Flash Mode:** `QIO 80MHz`
* **Flash Size:** `8MB (64Mb)` or `16MB` (depending on DevKit)
* **Partition Scheme:** `Huge APP (3MB No OTA/1MB SPIFFS)`
* **PSRAM:** `OPI PSRAM`
* **Upload Speed:** `921600`

---

## 6. On-Board Cellular & GNSS Module (Quectel EC200U-CN)

The **7Semi ESP32-S3 EC200U** board integrates a Quectel EC200U-CN 4G LTE Cat-1 modem connected to the ESP32-S3 via an internal UART. This provides the following built-in capabilities **without any external smartphone or WiFi**:

| Capability | Details |
|:---|:---|
| **Cellular Data** | 4G LTE Cat-1 (Bands: B1/B3/B5/B8 FDD, B34/B38/B39/B40/B41 TDD) |
| **Fallback** | GSM/GPRS (2G) for areas without 4G coverage |
| **SMS** | Send/receive SMS via AT commands over UART |
| **GNSS Positioning** | GPS, GLONASS, BeiDou, Galileo |
| **Protocols** | MQTT, TCP/IP, HTTP(S), FTP |
| **SIM Slot** | Micro SIM (Jio / Airtel / BSNL government SIM compatible) |
| **Power** | Max 5V via USB-C; modem managed by the 7Semi board's onboard regulator |

### Clinical Applications of Cellular + GPS

1. **Emergency SMS Alert:** When composite triage score ≥ 50 (CRITICAL), auto-send SMS with patient vitals + GPS coordinates to the nearest PHC / 108 ambulance.
2. **GPS-Tagged Records:** Every screening is geotagged automatically, enabling district health officers to create disease prevalence heatmaps.
3. **MQTT Telemetry Upload:** Push screening summaries to a cloud dashboard (when 4G available) for remote doctor review / teleconsultation.
4. **Offline-First, Sync-Later:** Store records in ESP32 NVS/LittleFS when offline → batch-upload via 4G when coverage is available.
