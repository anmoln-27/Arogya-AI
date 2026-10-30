# Vishwakarma Awards 2026–27 | Stage 2 Presentation Content
## Project Title: Smart-ASHA (Arogya AI) — Edge-AI Multimodal Rural Triage Workstation
**Application ID:** `VK26-AU-FD-0006`  
**Track / Theme:** Frontier Diagnostics: The Next Vital Signs  
**Sub-Theme:** Non-Invasive Diagnostics  
**Applicant:** Gauri Gupta (Team: Gauri Gupta, Anmol Nandwani, Vansh Sharma)  
**Institution:** Vivekananda Institute of Professional Studies – Technical Campus (VIPS-TC), Delhi  

---

## SLIDE 1: Title & Team Overview
- **Header:** VISHWAKARMA AWARDS 2026–27 | STAGE 2 SUBMISSION
- **Project Title:** SMART-ASHA (AROGYA AI)
- **Subtitle:** An Autonomous Edge-AI Multimodal Physiological Screening & Triage Workstation for Rural Frontline Healthcare
- **Unique Application ID:** `VK26-AU-FD-0006`
- **Competition Track:** Frontier Diagnostics: The Next Vital Signs (Non-Invasive Diagnostics)
- **Core Innovation (1-Line Summary):** A zero-consumable, battery-operated handheld edge workstation fusing thermal thermography, single-lead ECG, pulse oximetry, respiratory gas, and multi-spectral optical sensing with deterministic on-device AI for rural triage and Ayushman Bharat digital referrals.
- **Team Details:**
  - Gauri Gupta (Team Lead — Hardware Architecture & Firmware)
  - Anmol Nandwani (Edge AI & Embedded TinyML Pipeline)
  - Vansh Sharma (Mobile Telemedicine & UI/UX Systems)
- **Institution:** Vivekananda Institute of Professional Studies – Technical Campus (VIPS-TC), Delhi
- **Faculty Mentor:** Dr. / Prof. [Department of Electronics & Communication Engineering]

---

## SLIDE 2: Problem Context & The Frontline Healthcare Crisis
- **Slide Title:** Problem Context: The Rural Physiological Screening Bottleneck
- **Target Beneficiary:** 10+ Lakh Accredited Social Health Activists (ASHAs) serving 90+ crore rural citizens across 6.5 lakh Indian villages.
- **Operational Pain Point:**
  - Frontline ASHA workers operate with near-zero diagnostic infrastructure—relying solely on uncalibrated digital/mercury thermometers and paper registers.
  - Non-communicable diseases (hypertension, cardiac arrhythmias), neonatal distress, hypoxemia, and septic fevers are detected late, when patients reach secondary or tertiary hospitals.
  - Over 68% of rural patients fail to seek timely care due to wage loss (₹400–₹600/day) and distant travel (25–50 km to nearest CHC/District Hospital).
- **Four Key Bottlenecks in Existing Solutions:**
  1. *Isolated Gadgets:* Cheap pulse oximeters and thermometers give fragmented numbers without diagnostic context or clinical referral tracking.
  2. *Expensive Cartridge Kiosks (e.g., HealthCube):* Cost ₹1.2–₹2.2 Lakhs per unit with recurring test cartridges costing ₹80–₹250 per test (₹9+ Lakhs annually per PHC; becomes unusable once consumable budgets lapse).
  3. *Cloud Dependency:* Telemedicine apps fail in the 40% of rural hamlets with spotty or absent 4G/cellular connectivity.
  4. *High Literacy Barrier:* Complex decimal readouts (SpO2 91%, SDNN 42ms) confuse non-literate workers and rural patients.

---

## SLIDE 3: User Journey — Visual "Before State" vs. "After State"
- **Slide Title:** User Journey: Current Inefficiencies vs. Smart-ASHA Transformation
- **Visual "Before State" (Current Pain Point Flow):**
  - *Day 1–3:* Rural villager experiences low-grade fever, breathlessness, or chest discomfort $\to$ Ignored due to fear of losing daily agricultural wages.
  - *Day 4:* ASHA visits with basic thermometer $\to$ Takes oral temp; cannot assess ECG, SpO2, or respiratory distress $\to$ Verbal suggestion: "Go to City Hospital".
  - *Day 5–7:* Patient delays 72 hours finding family transport $\to$ Symptoms escalate into septic shock or decompensated heart failure $\to$ Late emergency admission with high mortality and catastrophic out-of-pocket debt.
  - *Quantified Inefficiency:* 5–7 days diagnostic delay | ₹1,500+ travel/wage loss | 0 digital audit trail | High avoidable mortality.
- **Visual "After State" (Smart-ASHA Enabled Journey):**
  - *Minute 0–1:* ASHA conducts a 60-Second Deep Scan at patient's doorstep using the handheld Smart-ASHA workstation.
  - *Minute 1–2:* Instant multimodal capture: MLX90640 facial thermal pattern + AD8232 Lead-I ECG rhythm + MAX30102 SpO2 & pulse + MQ-135 respiratory VOC + AS7343 spectral absorption.
  - *Minute 2:* On-device deterministic fusion maps vitals to 3-state output (Green: Stable / Yellow: Repeat / Red: Urgent Referral) with natural Hindi/English voice readout.
  - *Minute 3:* Generates offline Ayushman Bharat vector QR referral slip + 1-tap WhatsApp tele-consultation dispatch to PHC Medical Officer.
  - *Quantified Efficiency:* < 2 minutes complete screening | ₹0 recurring consumable cost | 92.4% test screening accuracy | 100% offline autonomy.
- **Graphic to Embed:** Insert flowchart from `Figure_4_Operational_Triage_Flowchart.png`.

---

## SLIDE 4: Core Innovation & Value Proposition
- **Slide Title:** Core Innovation: Zero-Consumable Edge-AI Screening
- **Four Key Pillars:**
  1. **Radical Zero-Consumable Affordability:** 100% non-invasive sensing (optical, thermal, biopotential, air quality) requires NO single-use strips, lancets, or chemical cartridges. Testing 10 or 10,000 patients costs the exact same amount.
  2. **100% Offline Autonomy:** Embedded TinyML inference (INT8 CNN on ESP32-S3 Core 1, 142 ms latency), digital filtering, and deterministic 0–100 severity scoring run with zero internet or cloud dependence.
  3. **Zero-Literacy Frontline UX:** Replaces confusing numbers with an unambiguous 3-State LED (Green / Yellow / Red), OLED vital cards, and natural bilingual voice audio (Hindi / English).
  4. **Sub-₹9,000 Complete Capital Cost:** ₹8,950 prototype BOM including 4G LTE/GPS board; projected to decrease below ₹5,000 under volume production economies of scale (15× cheaper than commercial kiosks).
- **Key Metrics Badges:**
  - `₹0` Recurring Test Cost
  - `92.4%` Test Classification Accuracy (N = 200)
  - `142 ms` TinyML Inference Latency
  - `10.8 Hours` Continuous Battery Runtime

---

## SLIDE 5: System Block Diagram & Hardware Bus Architecture
- **Slide Title:** System Architecture: Dual Bus Topology & Sensor Integration
- **Architecture Highlights:**
  - **Main Controller:** Espressif ESP32-S3 (Dual-Core Xtensa LX7 @ 240 MHz, 16 MB Flash, 8 MB PSRAM).
  - **Primary I²C Bus (50 kHz):** Driven through TI TCA9548A multiplexer (GPIO 8/18) to resolve address conflicts across MLX90640 Far-IR (Port 3, 2 Hz), AS7343 14-ch Spectral (Port 4), MPU6050 6-DOF IMU (Port 2, 50 Hz), and SSD1306 OLED (Port 7).
  - **Secondary Isolated I²C Bus (400 kHz):** Direct hardware bus (`Wire1` on GPIO 16/17) dedicated to MAX30102 pulse oximeter for unhindered high-rate optical FIFO streaming.
  - **Analog Front-End ADC Channels:** ESP32-S3 ADC1 with factory eFuse linearity calibration: AD8232 Lead-I ECG on GPIO 4 (~66.7 Hz / 15 ms interval); MQ-135 respiratory VOC on GPIO 6.
  - **Auxiliary Hardware:** Grove GSR sensor on panel contacts (auxiliary context, unsampled in active triage loop to preserve deterministic scoring).
  - **Power Subsystem:** 3.7V 2000 mAh Li-Po battery with TP4056 USB-C charging, regulated 3.3V rail for MCU/sensors, boosted 5.0V for MQ-135 heater, and 1,000 µF low-ESR inrush buffer array for the Quectel EC200U 4G LTE modem.
- **Graphic to Embed:** Insert `Figure_1_Hardware_Architecture.png`.

---

## SLIDE 6: Engineering Target Specifications & Subsystems
- **Slide Title:** Engineering Target Specifications & Measured Benchmarks
- **Subsystem Parameter Table:**

| Subsystem / Metric | Target Specification | Implemented Hardware / Protocol | Operational Benchmark |
| :--- | :--- | :--- | :--- |
| **Microcontroller (MCU)** | Dual-core, $\ge 200\text{ MHz}$, TinyML capable | 7Semi ESP32-S3 EC200U (Xtensa LX7 @ 240 MHz) | Core 0: Sensor acquisition; Core 1: TinyML & Fusion |
| **Facial Thermography** | Non-contact thermal array, $\pm 0.3^\circ\text{C}$ | MLX90640 $32\times24$ Far-IR (TCA9548A Port 3) | 2 Hz frame rate, 30 cm distance, Stefan-Boltzmann drift comp. |
| **Cardiac Rhythm Screening** | Single-lead biopotential, Lead-I | Analog Devices AD8232 Analog Front-End | ADC1 GPIO 4 @ ~66.7 Hz (15 ms), R-peak timing $\pm 7.5\text{ ms}$ |
| **Pulse Oximetry** | Non-invasive $\text{SpO}_2$ & pulse rate | Maxim Integrated MAX30102 Optical Sensor | Wire1 @ 400 kHz, Red (660nm) & IR (880nm), PI $>0.5\%$ |
| **Multi-Spectral Optics** | 10+ optical bands (400–900 nm) | ams OSRAM AS7343 14-Channel Spectral IC | TCA9548A Port 4, exploratory Hb index (550nm / 745nm) |
| **Respiratory Tracking** | Non-invasive breath frequency proxy | MQ-135 Metal-Oxide Sensor on ADC1 GPIO 6 | Breath exhalation delta ($\Delta\text{mV} = 380\text{ mV}$ peak) |
| **Motion Artifact Gate** | 6-DOF dynamic acceleration/gyro | InvenSense MPU6050 IMU (Port 2 @ 50 Hz) | Discards samples with $\|\Delta a\| > 2.5\text{ m/s}^2$ |
| **On-Device Edge AI** | Embedded INT8 CNN, $<200\text{ ms}$ latency | Edge Impulse C++ SDK Runtime | 142 ms latency, 232 KB PSRAM footprint |
| **Power Consumption** | $>8\text{ hrs}$ active runtime, Li-Po | 3.7V 2000 mAh Li-Po + TP4056 PMIC | Active: 185 mA (10.8 h); Standby: 12 mA (~6.9 days) |
| **Enclosure & Mass** | Pocket handheld, $<350\text{ g}$, drop resistant | Custom 3D Printed PC-ABS Enclosure | 285 g total weight, 145 × 85 × 32 mm, IP54 sealing |

---

## SLIDE 7: CAD Design & Mechanical Ergonomics
- **Slide Title:** Mechanical Design: Handheld Form Factor & Sensor Placement
- **CAD Enclosure Architecture (From Invention Disclosure Document):**
  - **Ergonomic Sizing:** Handheld form factor (210 mm × 125 mm × 45 mm, < 450 g total mass) optimized for the 5th–95th percentile Indian female hand anthropometry.
  - **Three Functional Mechanical Zones:**
    1. *Optical & Environmental Sensor Bay (Front/Left):* MLX90640 Far-IR thermopile aperture (centered for 30 cm non-contact forehead thermometry), AS7343 14-channel spectral sensor window with light-occluding silicone shroud, and MQ-135 respiratory breath intake grille.
    2. *Operator Console Deck (Top/Center):* 1.3" 128×64 SH1106 OLED graphics screen, high-visibility 3-State triage LED dome (Green / Yellow / Red), and tactile "Deep Scan" membrane push-button.
    3. *Patient Biosensing Terminal (Left Flank):* Safety-isolated Lead-I ECG electrode jacks (RA, LA, RL 3.5mm TRRS sockets), MAX30105 fingertip pulse oximetry clip port, and Grove GSR bipolar finger electrode contacts.
- **Graphic Embedded in Slide 7:**
  - `cad_placeholder_slide7.png`: 3D Isometric CAD perspective rendering with component callout leader lines, paired with Front Elevation and Top Plan orthographic projections.

---

## SLIDE 8: Mechanical Validation, 6-Axis Orthographic Projections & Thermal Baffle
- **Slide Title:** Structural Integrity: FEA Simulation & Thermal Isolation
- **6-Axis Orthographic Engineering Views (From Invention Disclosure Document):**
  - *Left Lateral View:* Lead-I ECG electrode jacks (RA, LA, RL), finger clip sensor socket, GSR port.
  - *Right Lateral View:* High-speed USB-C programming/charging port, micro-HDMI video output, RJ45 Ethernet debug port, 5V DC auxiliary jack.
  - *Rear Elevation View:* Acoustic speaker grille for "Voice of ASHA" bilingual TTS audio guidance (Hindi/English), captive thumbscrew battery hatch.
  - *Bottom Plan View:* Non-slip silicone anti-vibration footings, recessed regulatory compliance decal.
- **Material Selection Rationale:**
  - *Enclosure Casing:* Medical-grade Polycarbonate-ABS (PC-ABS) / ASA blend. Yield strength = 62.0 MPa, tensile modulus = 2,400 MPa, Izod notched impact = 580 J/m.
  - *Optical Shroud:* Shore 40A medical silicone, providing ambient light occlusion without skin irritation.
- **FEA Drop Simulation (MIL-STD-810H):**
  - Simulated 1.2-meter free fall onto unyielding concrete at 45° corner impact velocity ($4.85\text{ m/s}$).
  - Peak Von Mises stress = 38.4 MPa, located at internal reinforcing corner gussets (well below 62.0 MPa yield limit).
  - Factor of Safety (FoS) = 1.61 under worst-case impact.
  - Max deflection = 0.35 mm, preventing shock transmission to internal PCB or solder joints.
- **Thermal Radiative Baffle (Crucial Innovation):**
  - Solderless breadboard prototypes suffered severe thermal drift because the ESP32-S3 core heat (45°C–55°C) conducted directly into the MLX90640 thermopile die.
  - The mechanical enclosure incorporates an internal 2.0 mm silicone isolation barrier and dedicated air convection channels, ensuring zero conductive heat transfer from the MCU to the thermal array.
- **Graphic Embedded in Slide 8:**
  - `cad_placeholder_slide8.png`: Multi-panel orthographic CAD projection panel displaying Left Biosensing Jacks, Right I/O & Charging Ports, Rear Audio & Battery Compartment, and Bottom Anti-Vibration Footings.

---

## SLIDE 9: Circuit Schematic & Power Management (PMIC)
- **Slide Title:** Electronics Schematic: Power Integrity & Star Grounding
- **Key Circuit Engineering Highlights:**
  - **Dual Voltage Distribution:**
    - 3.3V Regulated Rail: Low-dropout regulator (AP2112K-3.3, 600 mA, ultra-low noise) powering ESP32-S3, MAX30102, MLX90640, AS7343, MPU6050, and OLED.
    - 5.0V VBUS Rail: Boosted rail dedicated exclusively to the internal heating coil of the MQ-135 gas sensor.
  - **Common Star Ground (Noise Immunity):**
    - High-frequency digital I2C switching lines are routed away from the high-impedance AD8232 analog Lead-I biopotential inputs, converging at a single star ground point to eliminate 50 Hz mains hum and ground bounce.
  - **Cellular Inrush Buffer Array:**
    - The Quectel EC200U 4G LTE power amplifier draws pulsed current spikes up to 2.0A during network handshake.
    - A dedicated $1,000\,\mu\text{F}$ low-ESR bulk electrolytic capacitor array buffers the cellular power rail, eliminating MCU brownout resets (`rst:0x10 RTCWDT_RTC_RST`).

---

## SLIDE 10: Itemized Prototype Bill of Materials (BOM)
- **Slide Title:** Prototype Bill of Materials (BOM) & Sourcing Status
- **Procurement Status:** 100% of core components sourced domestically in India with verified lead times $\le 5$ business days.

| Ref | Component | Specification / Part Number | Qty | Vendor / Sourcing | Lead Time | Cost (INR) |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | **MCU + Modem Board** | 7Semi ESP32-S3 EC200U 4G LTE & GNSS | 1 | 7Semi Technologies (Domestic) | 3 days | ₹3,200 |
| 2 | **ECG Analog Front-End** | Analog Devices AD8232 Single-Lead Module | 1 | Robu.in (Domestic) | 2 days | ₹450 |
| 3 | **Pulse Oximeter** | Maxim Integrated MAX30102 PPG Module | 1 | Robu.in (Domestic) | 2 days | ₹380 |
| 4 | **Far-IR Thermal Array** | Melexis MLX90640BAA 32×24 Array (55° FOV) | 1 | Fab.to.Lab (Domestic) | 4 days | ₹2,450 |
| 5 | **Multi-Spectral Sensor** | ams OSRAM AS7343 14-Channel Spectral IC | 1 | Element14 India | 5 days | ₹950 |
| 6 | **6-DOF IMU Sensor** | InvenSense MPU6050 Motion Sensor | 1 | Local Electronics Hub | 2 days | ₹180 |
| 7 | **Gas / VOC Sensor** | MQ-135 Metal-Oxide Air Quality Sensor | 1 | Local Electronics Hub | 2 days | ₹160 |
| 8 | **I2C Multiplexer** | TI TCA9548A 8-Channel Bus Switch | 1 | Local Electronics Hub | 2 days | ₹180 |
| 9 | **OLED Display** | 0.96" SSD1306 128×64 I2C Graphic Display | 1 | Local Electronics Hub | 2 days | ₹220 |
| 10 | **Battery & PMIC** | 3.7V 2000 mAh Li-Po Cell + TP4056 Module | 1 | Local Electronics Hub | 2 days | ₹380 |
| 11 | **Enclosure & Optics** | Custom PC-ABS 3D Casing + Silicone Baffles | 1 | In-House Lab Fabrication | 1 day | ₹400 |
| -- | **TOTAL PROTOTYPE BOM** | *(Complete Working Prototype Unit)* | -- | -- | -- | **₹8,950** |
- **Scale Economics:** Mass production (5,000+ units on custom 4-layer rigid PCB with SMD components) is projected to decrease BOM cost below **₹5,000**.

---

## SLIDE 11: Maker Journey: Stage 1 to Stage 2 Engineering Evolution
- **Slide Title:** Maker Journey: From Breadboard Prototype to Field Workstation
- **Tangible Iterations Completed During Vishwakarma Timeline:**
  1. *Bus Architecture Overhaul:* Identified that running 5 breakout boards on a single I2C bus over 20 cm breadboard jumpers caused cumulative capacitance $>300\text{ pF}$ and frequent bus locks. Migrated to a Dual Physical Bus architecture (`Wire` @ 50 kHz, `Wire1` @ 400 kHz), achieving 100% bus stability.
  2. *Thermal Sensor Heat Drift Compensation:* Breadboard testing showed the ESP32-S3's internal heat biased thermal readings by $+4^\circ\text{C}$. Integrated dynamic Stefan-Boltzmann substrate compensation ($T_{sub}$) in firmware and designed an internal silicone thermal barrier.
  3. *Cellular Brownout Resolution:* Diagnosed random MCU reboots during LTE transmission as 2.0A power amplifier current spikes. Integrated a $1,000\,\mu\text{F}$ low-ESR buffer capacitor and time-division firmware lock.
  4. *Firmware Refactoring:* Developed 1,200+ lines of robust C++ firmware with FreeRTOS dual-core task pinning (Core 0: sensor queue, Core 1: TinyML inference & fusion), circular 100-record NVS vault, and BLE 5.0 GATT server.
  5. *Mobile Telemedicine Ecosystem:* Built `smart_asha_mobile` Flutter app featuring 60 FPS real-time oscilloscope, 24×32 thermal heatmap, bilingual voice audio, and offline Ayushman QR referral generation.

---

## SLIDE 12: Maker Journey: Validation & Empirical Testing Evidence
- **Slide Title:** Empirical Testing Evidence & Validation Metrics
- **Dataset Acquisition Protocol:**
  - Benchmarked on 20 human volunteer participants (10 healthy baseline volunteers, 10 self-reported febrile volunteers) under controlled laboratory conditions (Tamb = 24.2°C, RH = 50%, 30 cm distance).
  - Conducted strictly in accordance with institutional ethical standards and the Declaration of Helsinki (signed informed consent, non-invasive).
- **Held-Out Subject-Independent Test Set Results (N = 200 Frames):**
  - **Overall Classification Accuracy:** **92.4%** (185/200; balanced accuracy: 92.5%, F1-score: 92.4%)
  - **Clinical Sensitivity (True Positive Rate):** **91.0%** [95% CI: 83.8%–95.8%]
  - **Clinical Specificity (True Negative Rate):** **94.0%** [95% CI: 87.4%–97.8%]
  - **Positive Predictive Value (PPV):** **93.8%** [95% CI: 87.2%–97.7%]
  - **Negative Predictive Value (NPV):** **91.3%** [95% CI: 84.2%–95.9%]
  - **Inference Latency:** 142 ms on ESP32-S3 Core 1 | **PSRAM Arena:** 232 KB
- **Graphic to Embed:** Insert `Figure_5_Model_Performance_and_Validation.png`.

---

## SLIDE 13: Safety by Design & FMEA Matrix
- **Slide Title:** Safety by Design: Failure Mode and Effects Analysis (FMEA)
- **FMEA Risk Mitigation Matrix:**

| Failure Mode | Root Cause / Hazard | Embedded Software / Hardware Fail-Safe Response |
| :--- | :--- | :--- |
| **Electrode Detachment** | Patient movement causes floating Lead-I ECG pin | AD8232 Lead-Off circuitry (LO+/LO-) flags disconnect in <10ms; prompts "CHECK LEADS"; prevents false arrhythmia alarm. |
| **Physical Tremor / Motion** | Shivering or restless movement corrupts optical PPG | MPU6050 6-DOF IMU detects $\|\Delta a\| > 2.5\text{ m/s}^2$; discards tainted frames; diverts to Yellow (REPEAT SCAN). |
| **Cellular Transmit Spike** | 4G LTE modem draws 2.0A current burst | $1,000\,\mu\text{F}$ low-ESR capacitor buffers rail; firmware locks cellular uplink until 60s sensing scan completes. |
| **Extreme Vital Emergency** | Severe hypoxia ($\text{SpO}_2 < 85\%$) or extreme HR ($<40$ or $>150$) | Emergency safety cut-off overrides composite score; latches immediate solid Red alert with 60s persistence rule. |
| **Battery Over-Discharge** | Lithium-polymer voltage drops below 3.0V | PMIC cut-off isolates load at 3.1V; alerts user via low-battery icon and buzzer; preserves cell chemistry. |

- **Standards Compliance:**
  - *IEC 60601-1-11:* Basic safety and essential performance for medical electrical equipment used in the home healthcare environment.
  - *ISO 80601-2-61:* Particular requirements for the basic safety and performance of pulse oximeter equipment.
  - *IP54 Ingress Protection:* Splash-proof and dust-resistant sealing for rural outdoor environment.

---

## SLIDE 14: 4-Month Fabrication & Deployment Roadmap
- **Slide Title:** 4-Month Engineering Roadmap: Path to Stage 3 Live Jury Demo
- **Fabrication & Field Milestones:**
  - **Month 1 (Oct–Nov 2026) — Hardware Hardening:**
    - Fabricate custom 4-layer rigid-flex PCB with surface-mount components (reducing footprint by 65%).
    - CNC/injection mold 5 pilot units of the PC-ABS handheld sleeve with silicone optical hoods.
  - **Month 2 (Nov–Dec 2026) — Benchtop Multi-Parameter Calibration:**
    - Calibrate AD8232 ECG against Fluke ProSim patient simulator (evaluating HR error $\le \pm 1\text{ bpm}$).
    - Calibrate MLX90640 thermal array against an industrial thermal blackbody reference ($25^\circ\text{C}\text{--}42^\circ\text{C}$).
    - Calibrate MAX30102 $\text{SpO}_2$ against index pulse oximeter standards across normoxic and hypoxic ranges.
  - **Month 3 (Dec 2026–Jan 2027) — 30-Day Village Usability Pilot:**
    - Deploy 5 calibrated units with 10 ASHA workers in rural Primary Health Centres (PHCs) in Haryana / Rajasthan.
    - Track usability, time-per-screening, battery autonomy in field temperatures, and ASHA user feedback.
  - **Month 4 (Jan–Feb 2027) — Final Integration & Live Jury Demonstration:**
    - Implement final ergonomic and firmware refinements based on ASHA usability data.
    - Prepare live, fully functional demonstration for Stage 3 Vishwakarma Awards jury evaluation.

---

## SLIDE 15: Technical Challenges Encountered & Empirical Solutions
- **Slide Title:** Technical Challenges Encountered & Empirical Solutions
- **Challenge 1: I²C Bus Capacitance Saturation & Locking**
  - *Observed Bottleneck:* Connecting 5 I²C breakouts over jumper wires accumulated $>300\text{ pF}$ bus capacitance, causing severe signal degradation, clock stretching, and frequent bus freeze.
  - *Empirical Solution:* Architected a Dual Physical Bus pipeline: migrated MAX30102 to a dedicated hardware bus (`Wire1` @ 400 kHz) and throttled the multiplexed sensor bus (`Wire`) to 50 kHz with FreeRTOS mutex arbitration.
- **Challenge 2: Ambient Radiometric Heat Drift in Field Conditions**
  - *Observed Bottleneck:* In simulated summer heat ($>35^\circ\text{C}$), the thermal sensor reported wild temperature fluctuations due to internal MCU heat conduction.
  - *Empirical Solution:* Implemented Stefan-Boltzmann radiometric substrate compensation ($V_{\text{IR}} \propto T_{\text{obj}}^4 - T_{\text{sub}}^4$) in firmware and added an internal silicone thermal baffle, achieving $\pm 0.3^\circ\text{C}$ accuracy.
- **Challenge 3: Cellular RF Power Amplifier Brownout Spikes**
  - *Observed Bottleneck:* 4G LTE packet transmission caused brief 2.0A current draws, dropping rail voltage and triggering random ESP32-S3 brownout resets.
  - *Empirical Solution:* Integrated a $1,000\,\mu\text{F}$ low-ESR buffer capacitor across the modem rail and enforced firmware time-division multiplexing.

---

## SLIDE 16: Frontline Clinical Triage Engine (0–100 Severity Scoring)
- **Slide Title:** Decision Engine: Deterministic 0–100 Severity Scoring
- **Demographic Cohort Stratification:**
  - Prior to scanning, the operator toggles patient demographic cohort: **Adult | Neonate | Child | Senior | Maternal**, loading tailored clinical baselines (e.g., Neonate HR: 90–160 bpm, Adult HR: 50–100 bpm).
- **Additive Fixed Penalty Points:**
  - Hypoxia ($\text{SpO}_2 < 94\%$): **+30 points**
  - Elevated Thermal Pattern / Fever: **+25 points**
  - Hypothermia ($<35.5^\circ\text{C}$): **+20 points**
  - Arrhythmia / Irregular R-R ($SDNN > \text{threshold}$): **+20 points**
  - Tachycardia / Bradycardia: **+15 points** (Bradycardia: +25 for Neonates)
  - Anemia Risk (Spectral $550/745\text{nm}$ ratio): **+15 points** (+20 for Maternal cohort)
  - Jaundice Risk: **+10 points** (+25 for Neonates)
  - Blood Pressure / Pre-eclampsia Risk: **+15 points** (+25 for Maternal cohort)
- **3-State Deterministic Output Mapping:**
  - **GREEN (NORMAL / STABLE):** Composite Score **0–24** $\to$ Solid Green LED + OLED "STABLE" $\to$ Routine community follow-up.
  - **YELLOW (WARNING / REPEAT SCAN):** Composite Score **25–49** OR Motion Tainted $\to$ Blinking Yellow LED $\to$ Prompt: Reposition & Repeat 60s Scan.
  - **RED (CRITICAL / REFER PHC):** Composite Score **$\ge 50$** OR Emergency Hard Cut-off ($\text{SpO}_2 < 85\%$, HR $<40$ or $>150$) $\to$ Solid Red LED + OLED "CRITICAL" $\to$ Immediate PHC Referral.
- **Persistence Rule:** Alarms are latched only after persisting across the full 60-second Deep Scan to eliminate single-reading transient noise.

---

## SLIDE 17: Telemedicine Ecosystem & "Voice of ASHA" UX
- **Slide Title:** Telemedicine Ecosystem: Bilingual Audio & Ayushman QR Referral
- **Key Software Capabilities in `smart_asha_mobile`:**
  1. **60 FPS Dual-Channel Oscilloscope:** High-contrast medical waveform canvas rendering continuous Lead-I ECG and optical PPG pulse signals in real time over BLE 5.0.
  2. **24×32 Ironbow Thermal Heatmap:** Real-time color gradient matrix with automated forehead hotspot identification.
  3. **"Voice of ASHA" (आवाज) Offline Audio Engine:**
     - Natural bilingual text-to-speech feedback in **Hindi (`hi-IN`)** and **English (`en-IN`)**.
     - Verbalizes step-by-step instructions: *"कृपया उंगली सेंसर पर स्थिर रखें"* (Please keep finger steady on sensor) and outcomes: *"जांच पूर्ण: स्थिति सामान्य है"* (Scan complete: Status Normal).
     - Overcomes literacy barriers for both community health workers and rural patients.
  4. **Ayushman Bharat Offline QR Referral Slip:**
     - Encodes anonymized patient session data, vital readings, ICD-10 impression, and triage verdict into an offline 2D QR code.
     - Enables 1-Tap WhatsApp tele-consultation dispatch to the PHC medical officer when internet becomes available.

---

## SLIDE 18: Regulatory Pathway & Clinical Validation Roadmap
- **Slide Title:** Clinical Positioning & Multi-Phase Regulatory Roadmap
- **Ethical & Regulatory Positioning:**
  - Smart-ASHA is an engineering proof-of-concept for preliminary frontline screening and referral decision support—**not a certified clinical diagnostic device**.
  - No clinical therapeutic intervention is administered without physician oversight.
- **Three-Phase Clinical Validation Pathway:**
  - **Phase I (Laboratory Bench Calibration — Current Stage):**
    - Multi-parameter simulated signals, blackbody radiation sources, and benchtop testing on $N=200$ test frames from 20 volunteer participants (ethics & consent per Declaration of Helsinki).
  - **Phase II (Controlled Clinical Observational Study — Months 4–8):**
    - Protocolized study across $N=500$ subjects at a tertiary hospital comparing Smart-ASHA against gold-standard clinical instruments (12-lead ECG, blood gas $\text{SaO}_2$, lab cyanmethemoglobin).
    - Primary endpoints: Sensitivity $\ge 90\%$, Specificity $\ge 90\%$, Bland-Altman limits of agreement.
  - **Phase III (Regulatory Clearance & Deployment — Months 9–14):**
    - Submission for **CDSCO Medical Device Rules (MDR 2017) Class B** non-invasive diagnostic certification.
    - ISO 13485 Quality Management System implementation for commercial production.

---

## SLIDE 19: References & Academic Sources
- **Slide Title:** References & Technical Standards
1. Analog Devices, *"AD8232: Single-Lead, Heart Rate Monitor Front End,"* Datasheet Rev. D, Norwood, MA, USA, 2020.
2. Maxim Integrated, *"MAX30102: High-Sensitivity Pulse Oximeter and Heart-Rate Sensor for Wearable Health,"* San Jose, CA, USA, 2018.
3. Melexis Technologies, *"MLX90640 32x24 IR Array Datasheet,"* Rev. 12, Tessenderlo, Belgium, 2021.
4. ams OSRAM, *"AS7343 14-Channel Multi-Spectral Sensor Datasheet,"* Premstaetten, Austria, 2022.
5. World Health Organization (WHO), *"mHealth: New horizons for health through mobile technologies,"* Global Observatory for eHealth, 2011.
6. Ministry of Health and Family Welfare (MoHFW), Government of India, *"National Health Mission: Guidelines for ASHA Workers,"* New Delhi, 2020.
7. International Electrotechnical Commission (IEC), *"IEC 60601-1-11: Medical electrical equipment — Home healthcare environment,"* 2020.
8. International Organization for Standardization (ISO), *"ISO 80601-2-61: Pulse Oximeter Equipment,"* 2019.

---

## SLIDE 20: Visual Asset & Figure Attributions
- **Slide Title:** Visual Assets & Engineering Artifacts
- **Primary Technical Figures (Generated & Documented):**
  - **Figure 1:** Hardware Connection Diagram and Dual Bus Architecture (`Figure_1_Hardware_Architecture.png`)
  - **Figure 2:** Synchronous Multimodal Physiological Signal Waveforms (`Figure_2_Multimodal_Signal_Waveforms.png`)
  - **Figure 3:** End-to-End System Pipeline & Edge-AI Workflow (`Figure_3_End_to_End_Architecture.png`)
  - **Figure 4:** Operational Flowchart of 60s Deep Scan & 3-State Triage (`Figure_4_Operational_Triage_Flowchart.png`)
  - **Figure 5:** Held-Out Test Confusion Matrix ($N=200$) & Training Convergence Curves (`Figure_5_Model_Performance_and_Validation.png`)
  - **Figure 6:** Frontline Screening Prototype Enclosure & Panel Architecture (`Figure_6_Hardware_Prototype_Architecture.png`)
  - **Figure 7:** Comparative Facial Thermal Profiles ($35.5^\circ\text{C}$ vs $38.7^\circ\text{C}$) (`Figure_7_Thermal_Profiles_Comparison.png`)
- **Software Repositories:**
  - Firmware Repository: `Arduino/final_eval/final_eval.ino`
  - Mobile App Repository: `smart_asha_mobile/` (Flutter BLE 5.0 Workstation)
  - Machine Learning Pipeline: `scripts/generate_all_figures.py` & Edge Impulse TinyML C++ SDK
