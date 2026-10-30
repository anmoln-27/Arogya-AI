# 🚀 Smart-ASHA: STM32H533RE Migration Suite
## Complete Architecture, Firmware & Hardware Porting for NUCLEO-H533RE

This directory contains the complete migration artifacts to transition the **Smart-ASHA (Arogya AI)** clinical workstation from the **ESP32-S3** to the **STMicroelectronics STM32H533RE (NUCLEO-H533RE)**.

---

### 📂 Directory Structure

```
STM/
├── README.md                                  # You are here: Master suite documentation
├── firmware/
│   ├── Smart_ASHA_STM32H533RE/
│   │   └── Smart_ASHA_STM32H533RE.ino         # Migrated, production-grade firmware
│   └── platformio.ini                         # Ready-to-compile PlatformIO configuration
├── hardware/
│   ├── nucleo_h533re_pinout_wiring.md         # Pin-by-pin master wiring guide
│   └── power_and_rf_decoupling.md             # Cellular 2.0A inrush current buffer design
├── ai_models/
│   └── edge_impulse_stm32_guide.md            # CMSIS-NN / STM32Cube.AI deployment guide
└── docs/
    └── MIGRATION_GUIDE_ESP32_TO_STM32H533RE.md # Full engineering translation dossier
```

---

### ⚡ Quick Summary of Porting Changes

| Subsystem | Original ESP32-S3 Architecture | Migrated STM32H533RE Architecture |
| :--- | :--- | :--- |
| **Microcontroller** | Dual-Core Xtensa LX7 @ 240 MHz | Single-Core Arm® Cortex®-M33 @ 250 MHz (with FPU & DSP) |
| **Development Board** | 7Semi ESP32-S3 EC200U 4G Carrier | STMicroelectronics **NUCLEO-H533RE** (Nucleo-64) |
| **Primary I²C Bus** | `GPIO 8` (SDA) / `GPIO 18` (SCL) @ 50 kHz | **`PB9` (I2C1_SDA) / `PB8` (I2C1_SCL)** @ 50 kHz -> TCA9548A Mux |
| **Secondary I²C Bus** | `GPIO 16` (SDA) / `GPIO 17` (SCL) @ 400 kHz| **`PB11` (I2C2_SDA) / `PB10` (I2C2_SCL)** @ 400 kHz -> MAX30105 Direct |
| **Lead-I ECG ADC** | `GPIO 4` (ADC1_CH3 via eFuse calibration) | **`PA0` (ADC1_INP1)** with 12-bit hardware oversampling |
| **MQ-135 Gas ADC** | `GPIO 6` (ADC1_CH5 via eFuse calibration) | **`PA1` (ADC1_INP2)** with 12-bit hardware oversampling |
| **Quectel 4G Modem** | Onboard UART pins | **`PA2` (USART2_TX) / `PA3` (USART2_RX)** @ 115200 baud |
| **Mobile App Sync** | Integrated on-chip BLE 5.0 GATT | **`PC4` (USART3_TX) / `PC5` (USART3_RX)** to external BLE co-processor |
| **Multitasking** | Asymmetric Dual-Core FreeRTOS | Preemptive Priority FreeRTOS with cooperative time-slicing |
| **Persistent Vault** | `Preferences.h` / NVS Flash Partition | Internal Flash Sector Emulation (or external I²C AT24C256) |

---

### 🛠️ Quick-Start Guide

1. **Hardware Assembly:** Follow [`hardware/nucleo_h533re_pinout_wiring.md`](file:///c:/Users/Acer/OneDrive/Desktop/DESKTOP%20VANSH/Smart%20Asha/STM/hardware/nucleo_h533re_pinout_wiring.md) to connect the sensor bus, display, modem, and analog electrodes to the Nucleo-64 Arduino headers.
2. **Firmware Upload:** 
   * Open Arduino IDE or PlatformIO.
   * Install the **STM32 Cores** by STMicroelectronics (`v2.7.1`+).
   * Select board: **Nucleo-64** -> **Nucleo H533RE**.
   * Compile and flash [`firmware/Smart_ASHA_STM32H533RE/Smart_ASHA_STM32H533RE.ino`](file:///c:/Users/Acer/OneDrive/Desktop/DESKTOP%20VANSH/Smart%20Asha/STM/firmware/Smart_ASHA_STM32H533RE/Smart_ASHA_STM32H533RE.ino).
3. **Serial Telemetry:** Open serial terminal at **115200 baud** on the ST-LINK USB-C port to monitor sensor convergence, PTT cuffless blood pressure, and triage classifications.

