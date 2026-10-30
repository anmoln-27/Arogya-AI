# 📑 Complete Migration Guide: ESP32-S3 to STM32H533RE
## Smart-ASHA Clinical Workstation Hardware & Firmware Re-Architecture

* **Author:** Smart-ASHA Systems Engineering Team  
* **Document Version:** v2.0 (Migration Final)  
* **Source Platform:** 7Semi ESP32-S3 EC200U 4G LTE Carrier Board  
* **Target Platform:** STMicroelectronics NUCLEO-H533RE (Arm® Cortex®-M33 @ 250 MHz)  
* **Baseline Code Reference:** [`Arduino/final_eval_v2/final_eval_v2.ino`](file:///c:/Users/Acer/OneDrive/Desktop/DESKTOP%20VANSH/Smart%20Asha/Arduino/final_eval_v2/final_eval_v2.ino)  
* **Target Code Reference:** [`STM/firmware/Smart_ASHA_STM32H533RE/Smart_ASHA_STM32H533RE.ino`](file:///c:/Users/Acer/OneDrive/Desktop/DESKTOP%20VANSH/Smart%20Asha/STM/firmware/Smart_ASHA_STM32H533RE/Smart_ASHA_STM32H533RE.ino)

---

### 1. Architectural Motivation & Scope

This dossier outlines the complete engineering migration required to transition the **Smart-ASHA multimodal diagnostic triage workstation** from the Espressif ESP32-S3 to the STMicroelectronics STM32H533RE microcontroller. 

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MIGRATION ARCHITECTURE                                 │
├─────────────────────────────────────────┬──────────────────────────────────────────────┤
│ FROM: ESP32-S3 (Current Baseline)       │ TO: STM32H533RE (Nucleo-64 Target)           │
├─────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Dual-Core 240 MHz Xtensa LX7          │ • Single-Core 250 MHz Arm Cortex-M33         │
│ • Integrated BLE 5.0 Radio              │ • External BLE Module (USART3 Bridge)        │
│ • Onboard Quectel 4G LTE Modem          │ • External EC200U Breakout (USART2 Bridge)   │
│ • Asymmetric Multi-Core FreeRTOS        │ • Single-Core Preemptive Priority FreeRTOS   │
│ • Internal NVS SPI Flash Partitions     │ • Flash Sector Emulation / I2C EEPROM        │
│ • 16 MB Flash / 512 KB SRAM             │ • 512 KB Flash / 272 KB SRAM (Strict INT8)   │
└─────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

### 2. Peripheral & Pin Translation Table

| Sensor / Functional Interface | ESP32-S3 Pin | STM32H533RE Pin | Bus / Peripheral | Mode & Configuration |
| :--- | :--- | :--- | :--- | :--- |
| **Primary I²C SDA** (TCA9548A Mux)| `GPIO 8` | **`PB9`** | `I2C1_SDA` | 50 kHz Open-Drain, 4.7kΩ Pull-Up |
| **Primary I²C SCL** (TCA9548A Mux)| `GPIO 18` | **`PB8`** | `I2C1_SCL` | 50 kHz Open-Drain, 4.7kΩ Pull-Up |
| **Secondary I²C SDA** (MAX30105) | `GPIO 16` | **`PB11`** | `I2C2_SDA` | 400 kHz Fast-Mode Isolated |
| **Secondary I²C SCL** (MAX30105) | `GPIO 17` | **`PB10`** | `I2C2_SCL` | 400 kHz Fast-Mode Isolated |
| **AD8232 ECG Biopotential Out** | `GPIO 4` (ADC1) | **`PA0`** | `ADC1_INP1` | 12-bit Analog In, Low-Noise |
| **MQ-135 Gas / Breath Out** | `GPIO 6` (ADC1) | **`PA1`** | `ADC1_INP2` | 12-bit Analog In |
| **Quectel EC200U TX** (Cellular) | Internal UART | **`PA2`** | `USART2_TX` | 115200 Baud AT Command Stream |
| **Quectel EC200U RX** (Cellular) | Internal UART | **`PA3`** | `USART2_RX` | 115200 Baud AT Command Stream |
| **External BLE Co-Processor TX** | N/A (Internal) | **`PC4`** | `USART3_TX` | 115200 Baud Binary Telemetry |
| **External BLE Co-Processor RX** | N/A (Internal) | **`PC5`** | `USART3_RX` | 115200 Baud Binary Telemetry |
| **Tri-Color Green Triage LED** | `GPIO 40` | **`PA5`** | `GPIO_Output` | Digital Out (Active High) |

---

### 3. Key Firmware Modifications Explained

#### 3.1 Dual-Core to Single-Core FreeRTOS Task Scheduling
In the ESP32-S3 firmware, tasks were pinned to separate cores using `xTaskCreatePinnedToCore`:
* **Core 0:** Ran the neural network inference in a continuous loop.
* **Core 1:** Polled the sensors at high speed.

On the single-core Cortex-M33, we replace core pinning with **preemptive priority scheduling**:
```cpp
// STM32 FreeRTOS Implementation:
// Priority 3 (High): Sensor sampling executes every 10 ms (100 Hz)
xTaskCreate(vSensorPollTask, "Sensors", 512, NULL, 3, &xSensorTaskHandle);

// Priority 1 (Low): AI inference runs in background and yields CPU
xTaskCreate(vAiInferenceTask, "AI_Infer", 512, NULL, 1, &xAiTaskHandle);
```
When an optical sample or ECG biopotential reading is due, FreeRTOS preempts the neural network for $150\,\mu\text{s}$, reads the sample into a circular buffer, and immediately resumes the inference. This eliminates optical sample drops without needing multicore hardware.

#### 3.2 Bridging the Missing BLE 5.0 Radio
Because the STM32H533RE has no wireless radio, the firmware forwards clinical packets out of `USART3` (`PC4`/`PC5`) to a tiny $1.50 BLE module (e.g. ESP32-C3-MINI or JDY-23):
```cpp
// Format transmitted at 10 Hz to external BLE module:
SerialBLE.printf("$ASHA,%lu,%s,%.1f,%.1f,%.2f,%d,%d,%s,%d,%s*\n",
  millis(), stateStr, tempC, spo2, bpm, sbp, dbp, tierStr, score, icd10Str);
```
The companion Flutter app (`smart_asha_mobile`) receives this stream and parses it identically to the native ESP32 BLE GATT characteristic.

---

### 4. Step-by-Step Benchtop Verification Checklist

- [ ] **Step 1: Smoke & Continuity Test**
  - Verify zero short circuits between `3.3V` and `GND`, or between `5V` and `3.3V` with a digital multimeter.
- [ ] **Step 2: ST-LINK Connection & Flash Test**
  - Plug USB-C into the ST-LINK connector on the Nucleo board.
  - Confirm the onboard ST-LINK COM port appears in Windows Device Manager.
  - Flash `Smart_ASHA_STM32H533RE.ino` via Arduino IDE or PlatformIO.
- [ ] **Step 3: I²C Bus Scan & Sensor Detection**
  - Open Serial Monitor at **115200 baud**.
  - Confirm serial reports:
    - `[OK] MLX90640 Radiometric Sensor Initialized.`
    - `[OK] AS7343 14-Channel Spectral Sensor Initialized.`
    - `[OK] MAX30105 Hemodynamic Suite Initialized on Wire1.`
- [ ] **Step 4: Optical Touch Auto-Wakeup**
  - Place a finger on the MAX30105 sensor aperture.
  - Verify that the IR channel triggers a transition from `IDLE` to `SCANNING` mode.
- [ ] **Step 5: Clinical Algorithm & Triage Display**
  - Complete a 60-second test scan.
  - Confirm the SH1106 OLED screen updates with BPM, SpO₂, PTT blood pressure, core temperature, and the ICD-10 diagnostic triage code.

