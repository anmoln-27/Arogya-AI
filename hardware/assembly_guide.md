# 🛠️ Smart-ASHA Hardware Assembly & Rebuild Guide

> **Note:** For the comprehensive, bench-level manual with full electrical smoke test procedures, troubleshooting matrices, and Star-Ground noise isolation guidelines, refer to:  
> 📖 [07_hardware_rebuild_and_reassembly_manual.md](file:///c:/Users/Acer/OneDrive/Desktop/DESKTOP%20VANSH/Smart%20Asha/Smart_ASHA_Complete_Dossier/07_hardware_rebuild_and_reassembly_manual.md)  
> Pinout reference: [03_hardware_setup_and_pinout_guide.md](file:///c:/Users/Acer/OneDrive/Desktop/DESKTOP%20VANSH/Smart%20Asha/Smart_ASHA_Complete_Dossier/03_hardware_setup_and_pinout_guide.md)

---

## Quick-Start Rebuild Sequence (Matching `final_eval_v2.ino`)

1. **Power & Ground Foundation:**
   - Establish a **Common Ground (Star Ground)** bus on breadboard/PCB connected to ESP32-S3 `GND`.
   - Distribute regulated `3.3V` from ESP32-S3 to power: TCA9548A, MAX30105, MLX90640, AS7343, MPU6050, SH1106 OLED, and AD8232.
   - Route `5.0V / VBUS` **ONLY** to the `VCC` pin of the MQ-135 Gas sensor heater coil.

2. **Primary I²C Bus (`Wire` @ 50 kHz):**
   - Connect **ESP32-S3 GPIO 8** -> TCA9548A `SDA`
   - Connect **ESP32-S3 GPIO 18** -> TCA9548A `SCL`
   - Connect TCA9548A `RST` -> `3.3V` (Mandatory pull-up)
   - Connect TCA9548A `A0, A1, A2` -> `GND` (Sets I²C address to `0x70`)

3. **Multiplexed Sensor Sub-Buses:**
   - **Port 2:** MPU-6050 6-Axis IMU (`SD2` -> SDA, `SC2` -> SCL, `AD0` -> GND, Address: `0x68`) *(Firmware has Port 1 fallback)*
   - **Port 3:** MLX90640 Thermal Vision (`SD3` -> SDA, `SC3` -> SCL, Address: `0x33`)
   - **Port 4:** AS7343 14-Channel Spectral Suite (`SD4` -> SDA, `SC4` -> SCL, Address: `0x39`)
   - **Port 7:** SH1106 128×64 OLED Display (`SD7` -> SDA, `SC7` -> SCL, Address: `0x3C`)
   - *(Ports 0, 1, 5, 6 remain unconnected)*

4. **Secondary Isolated I²C Bus (`Wire1` @ 400 kHz):**
   - Connect **ESP32-S3 GPIO 16** -> MAX30105 `SDA`
   - Connect **ESP32-S3 GPIO 17** -> MAX30105 `SCL`
   - Connect MAX30105 `VIN` -> `3.3V`, `GND` -> `GND`
   - *(Completely bypasses TCA9548A to prevent high-speed optical FIFO bottlenecks)*

5. **Calibrated Analog Channels (ESP32-S3 ADC1):**
   - Connect AD8232 ECG `OUTPUT` -> **ESP32-S3 GPIO 4** (`ADC1_CH3`)
   - Connect MQ-135 Gas `AOUT` -> **ESP32-S3 GPIO 6** (`ADC1_CH5`)
   - *(GSR and discrete LEDs are omitted in `final_eval_v2.ino`)*

6. **Cellular & GNSS Connections:**
   - Insert 4G LTE SIM Card into the 7Semi onboard Micro-SIM slot.
   - Connect LTE antenna to `MAIN` u.FL connector.
   - Connect active GNSS patch antenna to `GNSS` u.FL connector.

7. **Pre-Power Verification:**
   - Use multimeter continuity tester to confirm NO shorts between 3.3V and GND, or between 5V and 3.3V.
   - Power on via USB-C and open Serial Monitor at **115200 baud**.
   - Verify all 4 sensor suites report `[OK]`.
