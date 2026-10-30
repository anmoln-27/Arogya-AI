# 🔌 NUCLEO-H533RE Master Pinout & Hardware Wiring Guide
## Smart-ASHA Clinical Workstation Interface Specification

This document provides the definitive physical wiring map and electrical interface design for migrating the Smart-ASHA sensor suite to the **STMicroelectronics NUCLEO-H533RE (Nucleo-64)**.

---

### 1. Board Topology & Master Pinout Map

The diagram below maps Smart-ASHA sensor connections to the standard Arduino Uno V3 headers on the Nucleo-64:

```
                            NUCLEO-H533RE (Nucleo-64)
                                ┌────────────────┐
                                │   ST-LINK/V3E  │  (USB-C Debug & Power)
                                └───────┬────────┘
                                        │
           [TCA9548A SCL]   PB8  ───────┤ D15        NC ├───────
           [TCA9548A SDA]   PB9  ───────┤ D14     IOREF ├───────
                                        │ AVDD    RESET ├───────
                                        │ GND      3.3V ├───────  [3.3V System VCC]
           [MAX30105 SCL]   PB10 ───────┤ D13        5V ├───────  [5.0V MQ-135 Heater]
           [MAX30105 SDA]   PB11 ───────┤ D12       GND ├───────  [Common Ground]
           [User Green LED] PA5  ───────┤ D11       GND ├───────  [Common Ground]
                                        │ D10       VIN ├───────
                                        │ D9            │
                                        │ D8         A0 ├───────  PA0  [AD8232 ECG Out]
                                        │            A1 ├───────  PA1  [MQ-135 Gas Out]
           [BLE Bridge TX]  PC4  ───────┤ D2         A2 ├───────  PA4  [Auxiliary Analog]
           [BLE Bridge RX]  PC5  ───────┤ D3         A3 ├───────  PB0  [Reserved]
           [EC200U 4G TX]   PA2  ───────┤ D1 (TX)    A4 ├───────  PC1  [Reserved]
           [EC200U 4G RX]   PA3  ───────┤ D0 (RX)    A5 ├───────  PC0  [Reserved]
                                        └───────────────┘
```

---

### 2. Master Connection Matrix

| Subsystem / Sensor | Breakout Pin | NUCLEO-H533RE Pin | Header Name | Signal Type | Electrical Specification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Power Distribution** | `GND` | `GND` | Power | Star Ground | Common system ground bus |
| | `3.3V` | `3V3` | Power | Regulated 3.3V | Supplies all I²C sensors, display, & AD8232 |
| | `5.0V` | `5V` | Power | 5V Rail (VBUS) | Supplies **ONLY** MQ-135 internal heater coil |
| **Primary I²C Bus** | `SDA` | **`PB9`** | CN5 - Pin 9 (D14)| `I2C1_SDA` | Throttled to 50 kHz; 4.7kΩ pull-up to 3.3V |
| *(TCA9548A Multiplexer)*| `SCL` | **`PB8`** | CN5 - Pin 10 (D15)| `I2C1_SCL` | Throttled to 50 kHz; 4.7kΩ pull-up to 3.3V |
| | `RST` | `3V3` | Power | Logic High | Pulled high to 3.3V to prevent reset |
| | `A0, A1, A2` | `GND` | Power | Logic Low | Hardware I²C address: `0x70` |
| **Secondary Isolated I²C**| `SDA` | **`PB11`** | CN5 - Pin 6 (D12)| `I2C2_SDA` | High-speed 400 kHz Fast-Mode |
| *(MAX30105 Optical)* | `SCL` | **`PB10`** | CN5 - Pin 7 (D13)| `I2C2_SCL` | High-speed 400 kHz Fast-Mode |
| **Lead-I ECG (AD8232)** | `OUTPUT` | **`PA0`** | CN8 - Pin 1 (A0) | `ADC1_INP1` | 12-bit Analog In; shielded biopotential line |
| **Gas Sensor (MQ-135)** | `AOUT` | **`PA1`** | CN8 - Pin 2 (A1) | `ADC1_INP2` | 12-bit Analog In |
| **Quectel EC200U 4G LTE**| `TXD` | **`PA3`** | CN9 - Pin 1 (D0) | `USART2_RX` | 115200 baud AT commands |
| | `RXD` | **`PA2`** | CN9 - Pin 2 (D1) | `USART2_TX` | 115200 baud AT commands |
| **External BLE Module** | `TXD` | **`PC5`** | CN9 - Pin 4 (D3) | `USART3_RX` | 115200 baud binary telemetry stream |
| *(ESP32-C3 / JDY-23)* | `RXD` | **`PC4`** | CN9 - Pin 3 (D2) | `USART3_TX` | 115200 baud binary telemetry stream |
| **Triage Status LED** | Anode (+) | **`PA5`** | CN5 - Pin 5 (D11)| `GPIO_Output` | Digital Out (Green LED lights up if Score < 25) |

---

### 3. TCA9548A Multiplexer Sub-Bus Mapping (Primary `I2C1`)

All multiplexed slow sensors communicate through `I2C1` (`PB9`/`PB8`) via the TCA9548A switch (`0x70`):

| Multiplexer Channel | Connected Sensor / Device | I²C Address | Bus Speed | Description |
| :---: | :--- | :---: | :---: | :--- |
| **Port 0** | *Reserved* | — | — | Reserved for expansion |
| **Port 1** | *MPU6050 Auto-Detect Fallback* | `0x68` | 50 kHz | Auto-detected if Port 2 is inactive |
| **Port 2** | **MPU-6050 6-Axis IMU** | `0x68` | 50 kHz | Motion artifact rejection & tremor filter |
| **Port 3** | **MLX90640 Far-IR Camera** | `0x33` | 50 kHz | $24 \times 32$ Radiometric thermography |
| **Port 4** | **AS7343 14-Channel Spectral** | `0x39` | 50 kHz | Non-invasive ratiometric anemia & jaundice |
| **Port 5** | *Unused* | — | — | Disabled |
| **Port 6** | *Unused* | — | — | Disabled |
| **Port 7** | **SH1106 128×64 OLED Display** | `0x3C` | 50 kHz | Operator bedside triage screen |

---

### 4. Secondary Dedicated Bus (`I2C2` on `PB11`/`PB10`)

> [!IMPORTANT]
> The **MAX30105 hemodynamic optical suite** (`0x57`) is wired **directly to the STM32H533RE secondary hardware I²C controller (`I2C2`)**. It completely bypasses the multiplexer to prevent optical FIFO bottlenecks and ensure uninterrupted 400 kHz PPG pulse wave acquisition.

---

### 5. Cellular 4G LTE Power Decoupling & Inrush Buffer

When interfacing an external Quectel EC200U-CN modem to the Nucleo-H533RE:
1. **The Inrush Problem:** The EC200U draw current pulses of up to **$2.0\text{ A}$** during LTE transmit bursts. The Nucleo-64 onboard 3.3V LDO regulator **cannot supply $2.0\text{ A}$** and will trip or brown out the MCU.
2. **Mandatory Power Network:**
   * Power the EC200U from an independent **3.8V – 4.2V buck converter** (capable of 3.0A peak) or directly from a single-cell Li-Po battery.
   * Place a **$1000\,\mu\text{F}$ low-ESR electrolytic capacitor** in parallel with a **$100\,\text{nF}$ ceramic capacitor** directly across the modem `VBAT` and `GND` pins.
   * Connect all grounds together to a single **Star Ground** point at the Nucleo `GND` pin.

