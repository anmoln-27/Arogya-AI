# 🩺 Smart-ASHA Clinical Workstation Firmware v12.0 (`final_eval_v2.ino`)

This is the production-grade Arduino firmware for the **Smart-ASHA Edge-AI Healthcare Triage System**. It pushes the **4 Star Performers** (MAX30105, AS7343, MLX90640, AD8232) to their absolute clinical maximum, deeply integrates the **ESP32-S3** dual-core Xtensa LX7 architecture, enables **internal NVS flash patient storage**, and broadcasts live screening records over **Web-Bluetooth (BLE 5.0)** with **zero hardware rewiring**.

---

## 🌟 The 4 Star Performers: Clinical Capabilities

| Sensor | Role | Unlocked Capabilities in v12.0 |
|:---|:---|:---|
| **MAX30105** | **Hemodynamics** | • **Perfusion Index ($\text{PI} \%$):** Continuous peripheral blood volume monitoring ($AC/DC \times 100\%$). Detects cold shock, hypothermia, or vasoconstriction ($\text{PI} < 0.6\%$).<br/>• **Calibrated SpO₂ Curve:** Maps healthy baseline $R \approx 0.84$ into true $97\% - 99\%$ clinical range.<br/>• **High-Current Multi-Wavelength LED Drive:** Red, IR, and Green at $12.5\text{ mA}$ ($0x3F$).<br/>• **On-Chip Die Temperature:** Confirms genuine warm biological finger contact ($> 30^\circ\text{C}$). |
| **AS7343** | **Multi-Spectral** | • **Optical Dehydration Index ($NIR / F_{XL}$):** Water absorption ($855\text{ nm}$) relative to tissue baseline ($600\text{ nm}$) to flag pediatric & maternal dehydration.<br/>• **Ratiometric Hemoglobin Anemia Index ($F_5 / F_8$):** Eliminates melanin & pressure bias.<br/>• **Bilirubin Jaundice Index ($F_1 / FZ$):** Optical screening for neonatal & adult jaundice ($405\text{ nm}$).<br/>• **Full 14-Channel Spectral Fingerprint Vector.** |
| **MLX90640** | **Thermal Vision** | • **Dynamic $T_a$ Substrate Compensation:** Stefan-Boltzmann radiation correction for Indian heat ($35^\circ\text{C} - 40^\circ\text{C}$).<br/>• **Central Forehead ROI (16×8 grid):** Eliminates peripheral false heat.<br/>• **Bilateral Temporal Artery Asymmetry ($\Delta T = \|T_{\text{left}} - T_{\text{right}}\|$):** Flags unilateral cranial/vascular inflammation ($> 0.8^\circ\text{C}$).<br/>• **Central-to-Peripheral Thermal Shock Gradient:** Detects peripheral circulatory collapse. |
| **AD8232** | **Electrophysiology** | • **eFuse Calibrated Millivolts:** Factory ADC linearity compensation via `analogReadMilliVolts()`.<br/>• **Autonomic Tone Suite:** Computes **SDNN** (variance), **RMSSD** (parasympathetic tone), and **pNN50** (% adjacent beats $> 50\text{ ms}$).<br/>• **Leads-Off Guard & PPG Fallback:** Seamlessly shifts to optical finger pulse HRV when chest pads are disconnected, eliminating false arrhythmia penalties. |

---

## ⚡ ESP32-S3 Architecture & Data Telemetry

### 1. Web-Bluetooth (BLE 5.0) Wireless Export *(Zero App Installation)*
The firmware runs a native BLE GATT server advertising as **`Smart-ASHA-Pro`**:
- **Service UUID:** `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- **Characteristic UUID:** `beb5483e-36e1-4688-b7f5-ea07361b26a8` (Read + Notify)
- **JSON Telemetry Payload:** Upon scan completion, the device transmits a compact JSON string containing all vitals, triage score, and 4-star sensor metrics directly to any smartphone, tablet, or laptop browser (Chrome Web Bluetooth).

### 2. Internal NVS Flash Patient Vault & Configuration
- Uses ESP32 internal non-volatile storage (`Preferences.h`) to persist the last **100 patient screening records** (Score, Triage, Temp, SpO₂, PI, SDNN, Hb ratio, Dehydration ratio) plus active language settings.
- Records and language preferences survive battery depletion and reboots.
- **Serial Console Commands (115200 baud):**
  - Type `EXPORT` or `DUMP`: Dumps all stored patient records in clean CSV format.
  - Type `CLEAR`: Clears the NVS patient vault.
  - Type `LANG`: Displays current active language and available toggles.
  - Type `LANG EN`: Sets display language to English.
  - Type `LANG HI`: Sets display language to Hindi (Romanized OLED + Devanagari Serial/BLE).
  - Type `LANG BI`: Sets display language to Bilingual mode (EN + HI).
  - Type `HELP`: Lists all workstation serial commands.

### 3. Multilingual Clinical Engine (English + Hindi + Bilingual)
Built specifically for rural Indian ASHA field deployment:
- **OLED Display Rendering:** Uses crisp, ultra-legible Romanized Hindi (`[ UNGLI LAGAYEIN ]`, `STHIR RAHEIN!`, `JAANCH...`, `GAMBHIR (PHC)`, `SAMANYA`) that renders flawlessly without large font memory overhead.
- **Serial Console Output:** Prints full, authentic Devanagari Hindi (`स्मार्ट-आशा बहु-प्रणाली नैदानिक रिपोर्ट`, `गंभीर (PHC रेफर करें)`, `रक्त में ऑक्सीजन`, `कम रक्त प्रवाह / शॉक`, `एनीमिया जोखिम`) side-by-side with English.
- **Web-Bluetooth (BLE 5.0) JSON:** Transmits both English and UTF-8 Devanagari Hindi fields (`"triage"`, `"triage_hi"`, `"triage_rom"`, `"lang"`) so web and mobile apps can dynamically render native Hindi script.
- **Persistent NVS Memory:** Remembers language preference across power cycles.

### 4. Dual-Core Asymmetric Processing
- **Core 0:** Runs the 2D CNN vision model (`Smart_ASHA_2.0_inferencing`) with 32-byte SIMD Xtensa LX7 alignment.
- **Core 1:** Polling, digital filtering, NVS persistence, multilingual rendering, and OLED workstation UI.
- **Watchdog:** 15-second hardware task watchdog auto-recovery (`esp_task_wdt`).

---

## 🔌 Pinout & Wiring Matrix (Unchanged)

| Subsystem | ESP32-S3 Pins | Bus / Channel | Notes |
|:---|:---|:---|:---|
| **TCA9548A Multiplexer** | **GPIO 8 (SDA), GPIO 18 (SCL)** | `Wire` @ 50 kHz | Port 2: MPU6050, Port 3: MLX90640, Port 4: AS7343, Port 7: SH1106 OLED |
| **MAX30105 Pulse Oximeter** | **GPIO 16 (SDA), GPIO 17 (SCL)** | `Wire1` @ 400 kHz | Isolated private bus |
| **AD8232 ECG Sensor** | **GPIO 4** | Analog (`ADC1_CH6`) | Calibrated via `analogReadMilliVolts()` |
| **MQ-135 Gas Sensor** | **GPIO 6** | Analog (`ADC1_CH5`) | Calibrated via `analogReadMilliVolts()` |

---

## 🛠️ Arduino IDE Flashing Settings

- **Board:** `ESP32S3 Dev Module`
- **USB CDC On Boot:** `Enabled`
- **CPU Frequency:** `240MHz (WiFi)`
- **Partition Scheme:** `Huge APP (3MB No OTA/1MB SPIFFS)` ⚠️
- **PSRAM:** `QSPI PSRAM` (or `Disabled` if your module does not have external PSRAM)
- **Upload Speed:** `921600`
