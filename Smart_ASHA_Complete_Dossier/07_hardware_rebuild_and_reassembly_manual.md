# 🛠️ Smart-ASHA: Complete Hardware Rebuild & Reassembly Manual
## Master Step-by-Step Restoration Guide for Bench & Field Units

**Target Firmware:** `final_eval_v2.ino` (v12.0 Clinical Workstation Pro)  
**Target Controller:** 7Semi ESP32-S3 EC200U 4G LTE Smart Modem  
**Revision:** v4.0 (Bench Reassembly & Verification Standard)

---

## 1. Overview & System Pinout Architecture

This manual provides an exhaustive, step-by-step procedure to **completely dismantle, rebuild, wire, mechanically mount, and verify** the Smart-ASHA clinical diagnostic workstation from bare components.

Every pin, port, voltage rail, and bus assignment in this guide is **100% matched to `final_eval_v2.ino`**.

### Architecture Overview

```
                      +---------------------------------------------------------+
                      |         7Semi ESP32-S3 EC200U 4G LTE Smart Modem        |
                      | ┌───────────────────────────┐ ┌───────────────────────┐ |
                      | │ ESP32-S3 Dual-Core Xtensa │ │ Quectel EC200U-CN 4G  │ |
                      | │ Core 0: 2D CNN AI Vision  │ │ LTE Cat-1 + GNSS      │ |
                      | │ Core 1: Sensor Hub & BLE  │ │ (Internal UART Bus)   │ |
                      | └─────────────┬─────────────┘ └───────────────────────┘ |
                      +---------------|-----+-------+-------+-------------------+
                                      |     |       |       |
            +-------------------------+     |       |       +-------------------------+
            |                               |       |                                 |
   [Primary I²C: Wire]                      |       |                    [Secondary I²C: Wire1]
  GPIO 8 (SDA) / GPIO 18 (SCL)              |       |                   GPIO 16 (SDA) / GPIO 17 (SCL)
        @ 50 kHz                            |       |                             @ 400 kHz
            |                               |       |                                 |
            v                               |       |                                 v
   +-------------------+                    |       |                    +-------------------------+
   |   TCA9548A Mux    |                    |       |                    |        MAX30105         |
   |  (Address: 0x70)  |                    |       |                    |  Pulse / SpO2 / PI %    |
   +---------+---------+                    |       |                    |  (Dedicated Fast Bus)   |
     | | | | |                              |       |                    +-------------------------+
     | | | | +-- Port 7: OLED (SH1106)      |       |
     | | | |     (0x3C @ 128x64)            +-- GPIO 4 (ADC1_CH3): AD8232 ECG Analog Out
     | | | |                                |
     | | | +---- Port 4: AS7343 Spectral    +-- GPIO 6 (ADC1_CH5): MQ-135 Gas Analog Out
     | | |       (0x39 @ 14 Channels)       |
     | | |                                  +-- [Note: GSR is Omitted in final_eval_v2]
     | | +------ Port 3: MLX90640 Far-IR
     | |         (0x33 @ 24x32 Thermal)
     | |
     | +-------- Port 2: MPU6050 Motion IMU (0x68)
     |           [Firmware auto-detects Port 1 as fallback]
     |
     +---------- Port 0: Reserved / Unused
```

---

## 2. Complete Bill of Materials (BOM) & Color-Coding Standard

### Component Roster

| Item | Component | Module Model | Operating Voltage | Interface | Role in `final_eval_v2` |
|:---:|:---|:---|:---:|:---:|:---|
| **1** | Microcontroller | 7Semi ESP32-S3 EC200U | 5V (USB-C) / 3.3V logic | Dual Core 240MHz | System Controller & BLE 5.0 Server |
| **2** | I²C Multiplexer | TCA9548A Breakout | 3.3V (VCC) | Primary I²C (`Wire`) | Isolates 4 I²C sub-buses @ 50 kHz |
| **3** | Hemodynamic Suite | MAX30105 Optical Hub | 3.3V (VIN) | Secondary I²C (`Wire1`) | SpO2, Heart Rate, Perfusion Index (PI) |
| **4** | Thermal Vision | MLX90640 (24×32) | 3.3V (VIN) | TCA Port 3 | Core 0 AI Fever & Temporal Asymmetry |
| **5** | Spectral Sensor | AS7343 14-Channel | 3.3V (VIN) | TCA Port 4 | Anemia (Hb), Jaundice, Dehydration |
| **6** | Motion IMU | MPU6050 6-Axis | 3.3V (VCC) | TCA Port 2 (or 1) | Motion artifact rejection & chest tracking |
| **7** | System Display | SH1106 1.3" OLED | 3.3V (VCC) | TCA Port 7 | 128×64 Real-time clinical UI |
| **8** | ECG Front-End | AD8232 Single-Lead | 3.3V (3.3V) | GPIO 4 (ADC1_CH3) | Filtered ECG wave, SDNN, RMSSD, HRV |
| **9** | Respiratory Gas | MQ-135 Breath VOC | 5.0V (VCC) | GPIO 6 (ADC1_CH5) | Respiratory VOCs, metabolic tracking |
| **10**| LTE/GNSS Antennas | u.FL LTE + GPS Antenna | Passive/Active | u.FL connectors | Cellular telemetry & GPS tagging |

### Recommended Wire Color-Coding Convention

To prevent wiring errors during a rebuild, strictly adhere to this wire harness color code:

* 🔴 **RED:** `+3.3V` Main Logic Power Rail
* 🟠 **ORANGE / PURPLE:** `+5.0V / VBUS` Power Rail (Heater coil of MQ-135 only!)
* ⚫ **BLACK / BROWN:** `GND` Common System Ground
* 🟡 **YELLOW:** `SCL` (Clock Lines — Primary & Secondary)
* 🟢 **GREEN:** `SDA` (Data Lines — Primary & Secondary)
* 🔵 **BLUE:** Calibrated Analog Signals (`GPIO 4` for ECG, `GPIO 6` for Gas)
* ⚪ **WHITE:** Control lines / Reset pull-ups (`TCA RST` -> 3.3V)

---

## 3. Pre-Rebuild Safety & Workspace Preparation

Before starting disassembly or reassembly:

1. **Power Isolation:** Unplug USB-C cable and disconnect external Li-Po / 18650 battery packs. **Never rewire any I²C or analog pin with power applied.**
2. **Electrostatic Discharge (ESD):** The MLX90640 thermal sensor and AS7343 spectral photodiodes are highly sensitive to ESD. Touch a grounded metallic surface before handling.
3. **Tools Required:**
   - Digital Multimeter with continuity buzzer and DC voltage mode.
   - Breadboard or custom stripboard/PCB.
   - 25× Dupont jumper wires (Male-to-Female and Male-to-Male).
   - Wire label tape or fine-tip permanent marker.
   - Small flathead / Phillips screwdriver.

---

## 4. Phase-by-Phase Rebuild & Reassembly Procedure

### Phase 1: Power & Common Ground Distribution (The Foundation)

> **Avoid Ground Loops:** The AD8232 ECG sensor amplifies microvolt-level signals ($100\times$ gain). If high-current digital components (like the OLED or the MQ-135 heater) share a daisy-chained ground wire with the AD8232, digital switching noise will ruin the ECG waveform. Always build a **Star Ground** topology.

1. **Establish the Common Ground Bus:**
   - Connect `GND` from the ESP32-S3 to the central blue/negative rail of your breadboard or distribution bus.
   - Every single sensor ground must tie directly into this common rail.
2. **Establish the 3.3V Regulated Logic Rail:**
   - Connect the `3V3` pin of the ESP32-S3 to the central red/positive rail.
   - This rail powers: TCA9548A, MAX30105, MLX90640, AS7343, MPU6050, SH1106 OLED, and AD8232.
3. **Establish the 5.0V Heater Rail:**
   - Connect the `5V` (or `VBUS`) pin from the ESP32-S3 to an isolated 5V power bus.
   - **This rail connects ONLY to the VCC pin of the MQ-135 Gas Sensor.**
   - ⚠️ **DANGER:** Connecting 5V to the ESP32-S3 GPIOs, TCA9548A, or any 3.3V sensor will permanently destroy their I/O buffers.

---

### Phase 2: Installing the Primary I²C Hub (TCA9548A Multiplexer)

The TCA9548A multiplexer allows the ESP32-S3 to communicate with multiple devices sharing the same I²C address without address collisions.

```
       ESP32-S3 Pin                  TCA9548A Breakout Pin
       ┌───────────┐                 ┌───────────────────┐
       │   3.3V    ├────────────────►│ VCC               │
       │   GND     ├────────────────►│ GND               │
       │   GPIO 8  ├────────────────►│ SDA (Input)       │
       │   GPIO 18 ├────────────────►│ SCL (Input)       │
       │   3.3V    ├────────────────►│ RST (Active Low)  │  <-- Pull to 3.3V!
       │   GND     ├────────────────►│ A0, A1, A2        │  <-- Sets address to 0x70
       └───────────┘                 └───────────────────┘
```

1. Insert the TCA9548A module into the prototyping board.
2. Wire `VCC` -> Breadboard `3.3V Rail`.
3. Wire `GND` -> Breadboard `GND Rail`.
4. Connect **ESP32-S3 GPIO 8** -> **TCA9548A SDA**.
5. Connect **ESP32-S3 GPIO 18** -> **TCA9548A SCL**.
6. Connect **TCA9548A RST** -> **3.3V Rail** (Mandatory: leaving RST floating causes intermittent random bus resets).
7. Ensure Address pins **A0, A1, A2** are connected to **GND** (confirms hardware address `0x70`).

---

### Phase 3: Wiring Downstream Sensors to the TCA9548A Sub-Buses

Each sensor connects to its dedicated channel on the TCA9548A. Each channel has dedicated `SDx` (Data) and `SCx` (Clock) pins.

#### Channel 2: MPU-6050 6-Axis Motion & Respiratory Tracking
* **Power:** `VCC` -> 3.3V Rail | `GND` -> Common GND Rail
* **I²C Signals:**
  - `SDA` -> **TCA9548A SD2**
  - `SCL` -> **TCA9548A SC2**
* **Address Pin:** `AD0` -> GND (Selects default address `0x68`)
* *Firmware Note:* In `final_eval_v2.ino`, if Port 2 does not respond on boot, the driver automatically scans and switches to **Port 1** as a fallback.

#### Channel 3: MLX90640 Far-Infrared Thermal Vision Array
* **Power:** `VIN` -> 3.3V Rail | `GND` -> Common GND Rail
* **I²C Signals:**
  - `SDA` -> **TCA9548A SD3**
  - `SCL` -> **TCA9548A SC3**
* *Hardware Note:* The MLX90640 module contains onboard 4.7kΩ pull-up resistors to its VIN. Ensure leads are kept under 15 cm to prevent signal degradation at 50 kHz.

#### Channel 4: AS7343 14-Channel Multi-Spectral Optical Suite
* **Power:** `VIN` -> 3.3V Rail | `GND` -> Common GND Rail
* **I²C Signals:**
  - `SDA` -> **TCA9548A SD4**
  - `SCL` -> **TCA9548A SC4**
* *Orientation Note:* Mount facing the examination aperture with unobstructed view.

#### Channel 7: SH1106 1.3" Monochrome OLED Display
* **Power:** `VCC` -> 3.3V Rail | `GND` -> Common GND Rail
* **I²C Signals:**
  - `SDA` -> **TCA9548A SD7**
  - `SCL` -> **TCA9548A SC7**
* *Address Note:* Ensure the rear resistor on the OLED board is set to `0x78` (which resolves to 7-bit I²C address `0x3C`).

> **TCA Ports 0, 1, 5, 6:** Keep unconnected. Port 0 is reserved for future acoustic sensor ADC expansion.

---

### Phase 4: Wiring the Secondary Isolated I²C Bus (MAX30105)

The MAX30105 pulse oximeter handles high-speed red, infrared, and green optical sampling. To guarantee zero bus contention and prevent timing jitter, it is wired directly to the ESP32-S3's **secondary hardware I²C controller (`Wire1`)**, bypassing the multiplexer entirely.

```
       ESP32-S3 Pin                  MAX30105 Breakout Pin
       ┌───────────┐                 ┌───────────────────┐
       │   3.3V    ├────────────────►│ VCC / VIN         │
       │   GND     ├────────────────►│ GND               │
       │   GPIO 16 ├────────────────►│ SDA               │
       │   GPIO 17 ├────────────────►│ SCL               │
       │   N/C     │                 │ INT (Leave Open)  │
       └───────────┘                 └───────────────────┘
```

1. Connect `VCC` / `VIN` -> **3.3V Rail**.
2. Connect `GND` -> **Common GND Rail**.
3. Connect **ESP32-S3 GPIO 16** -> **MAX30105 SDA**.
4. Connect **ESP32-S3 GPIO 17** -> **MAX30105 SCL**.
5. Leave the `INT` (Interrupt) pin unconnected (`final_eval_v2.ino` polls over `Wire1` @ 400 kHz).

---

### Phase 5: Wiring Calibrated Analog Channels (AD8232 & MQ-135)

ESP32-S3 has dedicated **ADC1** channels that operate with factory eFuse calibration. In `final_eval_v2.ino`, both analog sensors are sampled via `analogReadMilliVolts()`.

#### 1. AD8232 Single-Lead Heart Rate / ECG Monitor
```
       ESP32-S3 Pin                  AD8232 Breakout Pin
       ┌───────────┐                 ┌───────────────────────────┐
       │   3.3V    ├────────────────►│ 3.3V                      │
       │   GND     ├────────────────►│ GND (Star ground point)   │
       │   GPIO 4  ├────────────────►│ OUTPUT (Analog Raw ECG)   │
       │   N/C     │                 │ LO+ (Leave Unconnected)   │
       │   N/C     │                 │ LO- (Leave Unconnected)   │
       │   N/C     │                 │ SDN (Shutdown - Leave Open)
       └───────────┘                 └───────────────────────────┘
```
* Connect **AD8232 3.3V** -> **3.3V Clean Rail**.
* Connect **AD8232 GND** -> **Star Ground**.
* Connect **AD8232 OUTPUT** -> **ESP32-S3 GPIO 4** (`ADC1_CH3`).
* *Software Leads-Off:* `LO+` and `LO-` are not wired to digital pins; `final_eval_v2.ino` monitors voltage thresholds and baseline fluctuations in software to detect open leads.

#### 2. MQ-135 Air Quality / Breath VOC Sensor
```
       ESP32-S3 Pin                  MQ-135 Breakout Pin
       ┌───────────┐                 ┌───────────────────────────┐
       │   5.0V    ├────────────────►│ VCC (Heater Supply)       │
       │   GND     ├────────────────►│ GND                       │
       │   GPIO 6  ├────────────────►│ AOUT (Analog Voltage)    │
       │   N/C     │                 │ DOUT (Digital Threshold)  │
       └───────────┘                 └───────────────────────────┘
```
* Connect **MQ-135 VCC** -> **ESP32-S3 5V (VBUS) Rail** (The internal $SnO_2$ heater requires 5V to reach operating temperature of ~200°C).
* Connect **MQ-135 GND** -> **Common GND Rail**.
* Connect **MQ-135 AOUT** -> **ESP32-S3 GPIO 6** (`ADC1_CH5`).
* Leave `DOUT` unconnected.

> **Sensor Omissions in v12.0:**
> - **GSR (Skin Conductance):** Omitted in `final_eval_v2.ino`. Do NOT connect GSR to GPIO 35 (which was a legacy ESP32 pin).
> - **Status LEDs (GPIO 25/26):** Omitted in `final_eval_v2.ino`. The full graphical triage interface is rendered on the OLED display and streamed over BLE 5.0.

---

### Phase 6: Cellular Modem & Antenna Connections (Quectel EC200U)

The 7Semi ESP32-S3 board features an onboard Quectel EC200U-CN Cat-1 4G LTE modem connected via internal hardware UART.

1. **Micro-SIM Card:**
   - Insert a valid 4G LTE SIM (Jio, Airtel, Vi, or BSNL 4G) into the onboard Micro-SIM card slot until it clicks into place.
2. **Antennas:**
   - **LTE Antenna:** Snap the flexible PCB / whip antenna u.FL connector onto the jack labeled **MAIN** or **LTE**.
   - **GNSS Antenna:** Snap the active ceramic patch antenna onto the jack labeled **GNSS** or **GPS**. Mount the ceramic patch facing upward towards the sky.

---

## 5. Mechanical Enclosure & Optical Layout Guidelines

To ensure diagnostic accuracy and avoid sensor crosstalk:

1. **Thermal Vision Isolation (MLX90640):**
   - Mount the MLX90640 on the front bezel of the enclosure facing outwards toward the patient's face.
   - **Keep it away from the MQ-135 sensor:** The MQ-135 heater dissipates heat (~800 mW) that will create local convection currents and corrupt thermal camera readings if placed within 6 cm.
   - Provide an unobstructed $55^\circ \times 35^\circ$ field of view.
2. **Finger Diagnostic Chamber (MAX30105 + AS7343):**
   - The MAX30105 optical window and the AS7343 multi-spectral sensor should be recessed inside a light-shielded finger clip or rubberized cradle.
   - Ambient light (fluorescent tubes, direct sunlight) introduces high 50Hz/100Hz ripple on the photodiode amplifiers.
3. **Cable Dressing:**
   - Keep the AD8232 analog lead wire (GPIO 4) twisted with a ground wire and routed away from the 50 kHz / 400 kHz I²C clock lines and the 4G LTE antenna.

---

## 6. Pre-Power Electrical "Smoke Test" Checklist

Before connecting USB-C power to the newly assembled workstation, perform these mandatory multimeter checks:

- [ ] **Continuity Check (Short Circuit Test):**
  - Set multimeter to continuity buzzer.
  - Probe between **3.3V Rail** and **GND Rail**. -> **Must NOT buzz (No short).**
  - Probe between **5.0V Rail** and **GND Rail**. -> **Must NOT buzz (No short).**
  - Probe between **3.3V Rail** and **5.0V Rail**. -> **Must NOT buzz (No short).**
- [ ] **Polarity Verification:**
  - Verify every sensor's `VCC` or `VIN` pin connects to the positive rail and `GND` connects to common ground.
  - Pay special attention to the MPU-6050 and OLED display pins (some OLED boards swap VCC and GND!).
- [ ] **Bus Isolation Test:**
  - Probe between **GPIO 8 (Wire SDA)** and **GPIO 16 (Wire1 SDA)**. -> **Must NOT be connected.**
  - Probe between **GPIO 18 (Wire SCL)** and **GPIO 17 (Wire1 SCL)**. -> **Must NOT be connected.**
- [ ] **Multiplexer Reset Pin:**
  - Confirm **TCA9548A RST** is firmly connected to **3.3V**.

---

## 7. Step-by-Step Initial Boot & Verification

### Step 1: Connect Serial Monitor
1. Plug the USB-C cable into the ESP32-S3 USB port and connect to your PC.
2. Open Arduino IDE or Serial Terminal at **115200 baud**.
3. Press the **EN / RESET** button on the ESP32-S3.

### Step 2: Verify Boot Log Sequence
The output **must** match the following exact startup banner:

```text
========================================================
 SMART-ASHA v12.0: CLINICAL WORKSTATION BOOTING        
========================================================
[OK] MPU-6050 Online on TCA Port 2
[OK] MLX90640 Thermal Vision Online on TCA Port 3
[OK] AS7343 14-Channel Spectral Suite Online on TCA Port 4
[OK] MAX30105 Hemodynamic Suite Online on Wire1 (16/17)
[OK] Core 0 Edge AI Vision Engine Launched
[OK] Web-Bluetooth (BLE 5.0) Service 'Smart-ASHA-Pro' Active
[OK] NVS Vault Online (0 Records) | Active Language: BILINGUAL (EN+HI)
========================================================
 SYSTEM READY: Type 'EXPORT', 'LANG EN/HI/BI' in console
========================================================
```

### Step 3: Diagnostic Troubleshooting Matrix

If any sensor fails to initialize, use this quick resolution table:

| Boot Message | Root Cause | Immediate Fix |
|:---|:---|:---|
| `[ERR] MLX90640 Failed on Port 3!` | Loose connection on TCA Port 3 or bad 3.3V power | Check SD3 and SC3 wiring. Verify MLX90640 VIN has 3.3V. |
| `[ERR] AS7343 Failed on Port 4!` | Wiring swapped or address mismatch | Check SD4 -> SDA and SC4 -> SCL. Ensure VIN is 3.3V. |
| `[ERR] MAX30105 Failed on Wire1!` | Wire1 disconnected or wired to TCA | Verify SDA is on **GPIO 16** and SCL is on **GPIO 17**. Ensure it is NOT plugged into TCA. |
| `[WARN] MPU-6050 Disconnected` | Loose wiring on Port 2 and Port 1 | Check SD2/SC2. Ensure MPU6050 AD0 pin is tied to GND. |
| OLED screen blank | TCA Port 7 wiring or incorrect OLED driver | Check SD7/SC7. Verify OLED address jumper is 0x78 (0x3C). |
| Continuous ESP32 Reboot / Panic | Short circuit or power deficit on 3.3V regulator | Check multimeter for 3.3V sag. Use quality 5V 2A USB-C power source. |

---

## 8. Clinical Functional Testing (Post-Rebuild Verification)

Once all sensors report `[OK]`, perform a complete live clinical screening cycle:

1. **Standby Verification (IDLE State):**
   - The OLED display shows:
     ```text
     SMART-ASHA v12.0
     BLE: READY   NVS: 0 recs
     [ FINGER / UNGLI ]
     ```
   - Open any Web-Bluetooth or BLE Scanner tool on a phone/laptop and search for `Smart-ASHA-Pro`. Confirm connection.
2. **Finger Placement & Auto-Wake:**
   - Place a finger on the MAX30105 sensor optical window.
   - The IR reflection value will cross `35,000` counts, and the system will automatically transition from `IDLE` to `SCANNING` state.
3. **Active 60-Second Clinical Scan:**
   - The OLED displays real-time ECG waveform in the middle window, live SpO2 %, heart rate (BPM), and a dynamic progress bar (`SCAN/JAANCH [=====>    ]`).
   - If the patient moves excessively, the MPU6050 triggers the motion rejection filter, displaying `HOLD STILL! / STHIR` and pausing interval collection.
4. **Thermal Camera Verification:**
   - Align the MLX90640 toward the subject's forehead at 20 cm distance.
   - Core 0 runs inference via Edge Impulse CNN on the 768-pixel thermal frame asynchronously.
5. **Results & Triage Screen:**
   - After 60 seconds, the device displays the composite triage verdict (`SAMANYA`, `CHETAVANI`, or `GAMBHIR (PHC)`), along with Hb estimate, Dehydration index, and HRV (SDNN).
   - The record is automatically saved to the persistent NVS flash vault.
6. **Data Export Test:**
   - In the Serial Monitor, type `EXPORT` or `DUMP`.
   - The system dumps the CSV record containing all stored patient parameters.

---

## 9. Master Hardware Reassembly Pinout Quick-Reference

Keep this table printed near the assembly workbench:

```
====================================================================================================
                        SMART-ASHA MASTER CONNECTION MATRIX (v12.0)
====================================================================================================
ESP32-S3 Pin       Target Device Pin        Bus / Function               Notes
----------------------------------------------------------------------------------------------------
3.3V               All Sensors VCC / VIN    3.3V Logic Power Rail        TCA, MAX30105, MLX, AS7343, MPU, OLED, AD8232
5.0V / VBUS        MQ-135 VCC               5V Heater Power Rail         Dedicated to MQ-135 heater ONLY
GND                All Sensors GND          Star Common Ground           Tied together to prevent ground loops
----------------------------------------------------------------------------------------------------
GPIO 8             TCA9548A SDA             Primary I²C (`Wire`)         50 kHz bus clock
GPIO 18            TCA9548A SCL             Primary I²C (`Wire`)         50 kHz bus clock
3.3V               TCA9548A RST             Reset Line Pull-up           Prevents floating resets
GND                TCA9548A A0, A1, A2      Address Configuration        Sets multiplexer to 0x70
----------------------------------------------------------------------------------------------------
TCA Port 2 (SD2/SC2) MPU-6050 (SDA/SCL)     Multiplexed I²C (0x68)       Primary IMU (Fallback: Port 1)
TCA Port 3 (SD3/SC3) MLX90640 (SDA/SCL)     Multiplexed I²C (0x33)       24x32 Thermal Vision Array
TCA Port 4 (SD4/SC4) AS7343 (SDA/SCL)       Multiplexed I²C (0x39)       14-Channel Multi-Spectral
TCA Port 7 (SD7/SC7) SH1106 OLED (SDA/SCL)  Multiplexed I²C (0x3C)       128x64 Clinical System Display
----------------------------------------------------------------------------------------------------
GPIO 16            MAX30105 SDA             Secondary I²C (`Wire1`)      400 kHz Dedicated Fast Bus
GPIO 17            MAX30105 SCL             Secondary I²C (`Wire1`)      400 kHz Dedicated Fast Bus
----------------------------------------------------------------------------------------------------
GPIO 4             AD8232 OUTPUT            Analog In (`ADC1_CH3`)       eFuse Factory Calibrated Millivolts
GPIO 6             MQ-135 AOUT              Analog In (`ADC1_CH5`)       eFuse Factory Calibrated Millivolts
----------------------------------------------------------------------------------------------------
Internal UART      Quectel EC200U-CN        4G LTE Modem Interface       Onboard 7Semi board connection
Micro-SIM Slot     4G SIM Card              Cellular Network             Jio / Airtel / Vi / BSNL
u.FL Jack 1        Main 4G Antenna          Cellular RF                  LTE Cat-1 data + SMS
u.FL Jack 2        GNSS Patch Antenna       Satellite RF                 GPS / GLONASS / BeiDou
====================================================================================================
```
