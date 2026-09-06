# 📁 Smart-ASHA: Complete Engineering & Architecture Dossier

Welcome to the consolidated engineering and architecture archive for the **Smart-ASHA** Edge-AI healthcare triage system. This directory contains the complete technical reports, setup guides, code deep-dives, and hardware post-mortems generated for the project.

---

## 📑 Archive Contents & Navigation

```
Smart_ASHA_Complete_Dossier/
├── 📄 README.md                                 ← You are here (Master Index)
├── 📄 01_codebase_and_architecture_explainer.md ← Line-by-line code explainer & system architecture
├── 📄 02_software_firmware_post_mortem.md       ← Dual Edge Impulse conflict post-mortem & resolutions
├── 📄 03_hardware_setup_and_pinout_guide.md     ← Pinout matrix, 7Semi 4G board wiring, and IDE config
├── 📄 04_hardware_limitations_and_drift.md      ← Power sag & 4G RF inrush, Delhi drift, and PCB checklist
├── 📄 05_sensor_maximum_potential_guide.md      ← Sensor & 4G/GPS untapped capabilities & Arduino C++ code
└── 📄 06_competitive_analysis_healthcube.md     ← Healthcube market teardown & differentiation strategy
```

---

### 1. [01_codebase_and_architecture_explainer.md](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Smart_ASHA_Complete_Dossier/01_codebase_and_architecture_explainer.md)
* **What it covers:**
  * Complete line-by-line architectural breakdown of the Python training, data cleaning, and Edge C++ stack.
  * System architecture reflecting the **7Semi ESP32-S3 EC200U 4G LTE Smart Modem** and integrated cellular/GPS telemetry.
  * Deep dive into [`utils/models.py`](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/utils/models.py) (`FeverCNN` tensor shapes: $1 \times 24 \times 32 \to 8 \times 12 \times 16 \to 16 \times 6 \times 8 \to 32 \to 2$).
  * GIGO cleaning filters in [`utils/clean_dataset.py`](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/utils/clean_dataset.py) ($>100\text{k}$ spikes and 5s/10s lead/tail cropping).
  * Physiological data augmentation in [`scripts/augment_fever_data.py`](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/scripts/augment_fever_data.py) ($+3.0^\circ\text{C}$ to $+4.5^\circ\text{C}$ offsets).
  * Edge Impulse INT8 quantization calibration using [`scripts/combine_all_thermal_data.py`](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/scripts/combine_all_thermal_data.py).

---

### 2. [02_software_firmware_post_mortem.md](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Smart_ASHA_Complete_Dossier/02_software_firmware_post_mortem.md)
* **What it covers:**
  * Root cause analysis of why two Edge Impulse libraries cannot compile concurrently in Arduino IDE ("The Twin Problem").
  * Hardware CPU panic analysis: **`Guru Meditation: LoadStoreAlignment (0x9)`** caused by array dimension mismatch ($768$ vs $18$) on Xtensa LX7 SIMD loads.
  * ROM bootloop explanation: **`rst:0xc (RTC_SW_CPU_RST)`** triggered by static SRAM depletion prior to `setup()`.
  * I²C bus deadlock: **`ESP_ERR_INVALID_STATE [259]`** multi-core race conditions on the TCA9548A multiplexer.
  * Exact mathematical equations for deterministic triage (SDNN Arrhythmia variance, $SpO_2$ averaging, and AS7343 integration timing: $t_{int} = (\text{ATIME}+1)(\text{ASTEP}+1) \times 2.78\,\mu\text{s}$).

---

### 3. [03_hardware_setup_and_pinout_guide.md](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Smart_ASHA_Complete_Dossier/03_hardware_setup_and_pinout_guide.md)
* **What it covers:**
  * Complete Master Pinout Table for **7Semi ESP32-S3 EC200U 4G LTE Smart Modem** (ESP32-S3 + Quectel EC200U-CN 4G/GNSS).
  * Dual-I²C physical lane routing:
    * Primary `Wire` (Pins 8/18 @ 50 kHz) $\to$ TCA9548A Multiplexer (`0x70`).
    * Secondary `Wire1` (Pins 16/17) $\to$ Dedicated MAX30105 pulse oximeter lane.
  * Multiplexer channel map (Port 2: MPU6050, Port 3: MLX90640, Port 4: AS7343, Port 7: SH1106 OLED).
  * Quectel EC200U-CN internal UART communication, SIM slot, and GNSS antenna connections.
  * Arduino IDE compilation settings (OPI PSRAM, Huge APP 3MB partition, QIO 80MHz, 240MHz CPU).

---

### 4. [04_hardware_limitations_and_drift.md](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Smart_ASHA_Complete_Dossier/04_hardware_limitations_and_drift.md)
* **What it covers:**
  * Power rail current starvation & **Quectel EC200U 4G LTE RF transmission bursts (up to $2.0\text{ A}$ peak)** exceeding USB limits, resolved via bulk low-ESR decoupling ($470\,\mu\text{F} - 1000\,\mu\text{F}$) and $5\text{V}/2\text{A}$ external / LiPo supply.
  * Delhi ambient environment ($>35^\circ\text{C} - 40^\circ\text{C}$) radiometric drift: Substrate heat conduction ($V_{IR} \propto T_{obj}^4 - T_{sub}^4$), resolved via high-watermark peak extraction.
  * Breadboard jumper capacitance ($C_b > 300\text{ pF}$) and parallel pull-up resistor distortion.
  * 5-point transition checklist from breadboard prototype to 4-layer rigid-flex Stethoscope Sleeve.

---

### 5. [05_sensor_maximum_potential_guide.md](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Smart_ASHA_Complete_Dossier/05_sensor_maximum_potential_guide.md)
* **What it covers:**
  * Sensor-by-sensor breakdown of **what is currently used** vs. **what untapped capabilities** exist in the same hardware.
  * **MLX90640:** Dynamic `getTa()` substrate compensation, emissivity tuning, ROI forehead extraction, multi-frame temporal averaging.
  * **AS7343:** Full 14-channel wavelength map showing clinical relevance of every band, F5/F8 ratiometric anemia, FZ-band jaundice screening, ambient light rejection via Clear/Flicker channels.
  * **MAX30105:** Green LED PPG for BPM, built-in die temperature sensor, proper quadratic SpO₂ calibration, proximity mode auto-wake.
  * **AD8232:** Lead-off detection (LO+/LO−), IIR bandpass filter coefficients, adaptive R-peak threshold, ST-segment ischemia flagging.
  * **MQ-135:** Breath rate counting, warm-up compensation, resistance-to-PPM conversion.
  * **MPU6050 (0% utilized):** Motion artifact rejection, chest-wall respiratory rate, fall detection, posture detection.
  * **Quectel EC200U (4G LTE / GPS):** Direct SIM-based cloud uploads, automated GPS geotagging, emergency SMS broadcast to nearest PHC/108 ambulance.
  * **ESP32-S3:** Hardware timer ISR, light sleep, eFuse ADC calibration, PSRAM allocation, NVS patient storage.
  * **System-Level:** Composite triage severity score, BLE Web-Bluetooth export, watchdog timer.
  * Capability utilization dashboard showing each sensor's current vs. potential usage percentage.

---

### 6. [06_competitive_analysis_healthcube.md](file:///c:/Users/Acer/OneDrive/Desktop/Smart%20Asha/Smart_ASHA_Complete_Dossier/06_competitive_analysis_healthcube.md)
* **What it covers:**
  * Comprehensive competitor teardown of **Healthcube** (HealthCubed India Pvt Ltd, funded by Acumen/Gates Foundation).
  * **Cost Asymmetry:** Prototype BOM of **₹12,000** (production target: **₹6,000 – ₹8,000**) vs. Healthcube's **₹1,19,000** unit price (10–15× cost advantage).
  * **The Consumable Trap:** Healthcube charges ₹50–₹200+ per test in disposable cuvettes/strips (₹9,00,000/yr consumable TCO + biohazard waste), while Smart-ASHA is **100% non-invasive with zero consumables and zero recurring cost**.
  * **Hardware Connectivity Moat:** Smart-ASHA's 7Semi board features **built-in 4G LTE Cat-1 + GNSS positioning**, enabling standalone emergency SMS and geotagging without requiring a separate smartphone (Healthcube requires an external smartphone/tablet).
  * **Form Factor & Usability:** Pocket-sized single-hand operation vs. Healthcube's 1.7 kg box requiring tabletop setup, finger pricks, and blood handling.
  * **Strategic Differentiation Playbook:** Six concrete moats (Consumables, Price, Edge-AI, Standalone Cellular, Real-time UX, Infection Control) and a phased market entry strategy for NHM/CSR deployment.

