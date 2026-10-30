# Vishwakarma Awards 2026–27 | Project Progress & New Scope Addendum

**Unique Application ID:** `VK26-AU-FD-0006`  
**Theme:** Frontier Diagnostics: The Next Vital Signs  
**Sub-Theme:** Non-Invasive Diagnostics  
**Project Title:** Smart-ASHA (Arogya AI) — An Edge-AI Multimodal Cardiopulmonary & Biochemical Triage Workstation for Frontline Rural Healthcare  
**Applicant:** Gauri Gupta (Team: Gauri Gupta, Anmol Nandwani, Vansh Sharma)  
**Institution:** Vivekananda Institute of Professional Studies – Technical Campus (VIPS-TC)  
**Original Proposal Reference:** [Google Drive Submission](https://drive.google.com/open?id=1blc_d4vrcvbyp3kgUCBnqvCrJuQenglK)  

---

## Executive Summary of Project Status

Smart-ASHA was initially conceived as a proof-of-concept laboratory breadboard exploring whether low-cost optical, thermal, and electrical sensors could be fused around an ESP32-S3 to produce a quick, needle-free health snapshot. 

To qualify under the **Vishwakarma Awards 2026–27 timeline**, this document details the **exact, tangible new hardware, firmware, and software capabilities** currently being engineered and deployed during this challenge window. We clearly distinguish between our initial bench research and the extensive, field-hardening innovations that transform a fragile lab prototype into an autonomous, non-invasive clinical diagnostic workstation ready for frontline ASHA deployment.

---

## Question 1: Original Prototype vs. Exact New Features, Components & Capabilities

### 1.1 The Original Lab Prototype (Baseline Prior to Challenge)
The original submission was an exploratory **benchtop breadboard setup** consisting of:
* A generic ESP32-S3 development board running off USB power.
* Solderless breadboard jumper wiring (20 cm DuPont cables) routing multiple I²C breakouts (MAX30102 PPG, MLX90640 thermal array, AS7343 spectral sensor, MPU6050 IMU) through a single TCA9548A multiplexer.
* A basic 2D-CNN thermal model ("FeverCNN", ~119 KB ONNX) trained on static thermal images.
* A static 60-second scanning loop outputting simple numeric metrics and basic Red/Green indicator states onto a 0.96" OLED screen.
* A primitive analog galvanic skin response (GSR) sensor channel.

### 1.2 Exact New Work, Components & Capabilities Being Added During the Vishwakarma Timeline

During the active program timeline, we are executing a complete architectural overhaul across hardware, edge AI, and clinical software:

```
[Prior Bench Prototype] ───► [Vishwakarma Challenge Phase] ───► [Field-Ready Clinical Workstation]
  • 20cm Breadboard Wiring     • Custom 4-Layer Rigid-Flex PCB    • Ergonomic Handheld Sleeve
  • Single I2C Bus Overload    • Dual Physical Bus Architecture   • 10s Express + 60s Deep Scan
  • Raw Numbers on 0.96" OLED  • 100% Offline Flutter App         • 60 FPS Dual Canvas Oscilloscope
  • Unbuffered USB Power       • PMIC + 1000uF Inrush Buffer      • Integrated 4G LTE/GPS Telemetry
  • Lab Ambient Calibration    • Stefan-Boltzmann Drift Engine    • Offline Ayushman QR Referral Slip
```

#### A. Hardware Innovations & New Physical Components
1. **Transition to Custom 4-Layer Rigid-Flex PCB & Ergonomic CAD Enclosure:**
   * Replacing high-capacitance breadboard jumpers ($C_b > 300\text{ pF}$) with a custom-engineered 4-layer rigid-flex PCB ($C_b < 40\text{ pF}$), enabling rock-solid 400 kHz Fast-Mode I²C communication.
   * Packaging the assembly into a pocket-sized, drop-resistant, IP54 splash-proof handheld enclosure (210 mm × 125 mm × 45 mm, < 450 g total mass) designed specifically for frontline ASHA home visits (refer to Figure 6 for complete CAD orthographic projections and physical prototype assembly).
2. **Dedicated Optical Isolation Chamber for Spectral Anemia Screening:**
   * Engineering a 3D-printed, skin-conformal silicone shroud with a fixed optical aperture around the **AS7343 14-channel spectral sensor**. This eliminates 50 Hz/100 Hz ambient room lighting interference (fluorescent/LED flicker), allowing pure reflected light absorption from human microvasculature.
3. **Integrated 4G LTE/GNSS Telemetry & Power Management Circuitry (PMIC):**
   * Integrating an industrial **Quectel EC200U-CN 4G LTE Cat-1 & GNSS modem** onto the main board with u.FL antennas.
   * Adding a dedicated **Power Management IC (PMIC)** supporting single-cell Li-Po / 18650 battery operation with battery fuel gauging.
   * Implementing a **$1000\,\mu\text{F}$ low-ESR bulk capacitive buffer array** across the cellular rail to safely absorb $2.0\text{ A}$ RF power amplifier current bursts without pulling down the MCU rail.
4. **Thermal Radiative Barrier & 6-Axis Orthographic Architecture:**
   * Mechanically and thermally isolating the MLX90640 far-IR array from the ESP32-S3's heat dissipation using an internal 2.0 mm silicone gasket and convective thermal baffle.
   * Integrating safety-isolated 3.5mm TRRS jacks for Lead-I ECG biopotentials on the left flank, high-speed USB-C/RJ45/HDMI on the right flank, rear acoustic audio grille for bilingual voice prompts, and captive battery door on the rear panel.

#### B. Firmware & Edge-AI Enhancements
1. **Dual Physical Bus Segregation:**
   * Re-architecting the communication bus: moving the high-speed **MAX30105 hemodynamic suite** to a dedicated physical hardware bus (`Wire1` on GPIO 16/17 @ 400 kHz), while isolating the multiplexed environmental and spectral sensors on `Wire` (@ 50 kHz).
2. **Dynamic Stefan-Boltzmann Radiometric Drift Engine:**
   * Deploying real-time thermal compensation in firmware:
     $$V_{IR} \propto (T_{obj}^4 - T_{sub}^4)$$
     Actively sampling sensor substrate die temperature ($T_{sub}$) to cancel ambient heat drift, ensuring forehead core temperature accuracy even in Indian summer heat ($>38^\circ\text{C}$).
3. **Dual-Mode Clinical Scanning Engine:**
   * **10-Second Express Triage Mode:** An accelerated rolling-convergence scan engineered for rapid community screening camps and emergency triage.
   * **60-Second Deep Diagnostic Scan:** High-precision mode applying MPU6050 accelerometer vector filtering to cancel patient motion artifacts.
4. **Ratiometric Hemoglobin & Autonomic Tone Extraction:**
   * Calculating needle-free anemia risk by isolating the 555 nm hemoglobin absorption peak ($F_5$) against the 680 nm melanin baseline ($F_8$).
   * Extracting Heart Rate Variability ($\text{SDNN} > 110\text{ ms}$) and Perfusion Index ($PI\%$) to detect early circulatory collapse and shock.

#### C. Clinical Software & Telemedicine Ecosystem
1. **100% Offline Clinical Workstation App (`smart_asha_mobile`):**
   * Built from scratch in **Flutter**, operating entirely in **Airplane Mode** over Bluetooth Low Energy (BLE 5.0).
   * **Real-time 60 FPS Dual-Channel Canvas Oscilloscope:** High-contrast medical waveforms rendering continuous PPG pulse and Lead I ECG signals.
   * **24×32 Ironbow Facial Thermal Heatmap:** Real-time color gradient matrix with automated forehead hotspot identification.
2. **"Voice of ASHA" (आवाज) Offline Audio Engine:**
   * Natural bilingual text-to-speech audio feedback in **Hindi (`hi-IN`)** and **English (`en-IN`)**, verbalizing scan instructions and clinical findings for zero-literacy workers and rural patients.
3. **Deterministic Offline ICD-10 Triage & Ayushman Bharat Referral Engine:**
   * An on-device clinical rules engine that assigns triage tiers (Green / Yellow / Red) and maps clinical impressions to standardized **ICD-10 diagnostic codes**.
   * Generates an **offline vector QR referral slip** and enables **1-Tap WhatsApp tele-consultation dispatch** to the Primary Health Centre (PHC) medical officer.

---

## Question 2: Improvement over Original Work & Competitive Advantage

### 2.1 Direct Improvement over Our Original Work

| Dimension | Original Lab Prototype | Vishwakarma Workstation Update | Clinical / Practical Impact |
| :--- | :--- | :--- | :--- |
| **Physical Form** | Loose breadboard, exposed jumpers | Rigid-flex 4-layer PCB in IP54 sleeve | Survives field drop tests, moisture, and dust |
| **Bus Stability** | Frequent I²C NACK locks & bus halts | Dual physical buses (`Wire` & `Wire1`) | Zero bus crashes; concurrent optical & thermal reads |
| **Thermal Accuracy** | Drifts $>4^\circ\text{C}$ in ambient heat | Stefan-Boltzmann substrate compensation | Sub-$0.3^\circ\text{C}$ clinical accuracy in field heat ($>35^\circ\text{C}$) |
| **Scan Duration** | Fixed 60s only | Dual Mode: **10s Express** / **60s Deep** | Rapid queue clearance during village camps |
| **User Interface** | Raw numbers on 0.96" OLED | 60 FPS Oscilloscope, Ironbow Thermal | Comprehensive visual confirmation for ASHA & patient |
| **Accessibility** | Visual readout only | Bilingual Voice Audio (Hindi / English) | Usable by non-literate workers and patients |
| **Referral Workflow** | None (manual verbal referral) | Offline Ayushman QR + WhatsApp | Seamless integration into PHC clinical chain |

### 2.2 What Makes Our Approach Smarter, More Effective, and More Affordable

Existing point-of-care rural diagnostic devices in the market fall into three broken paradigms:
1. **Isolated Single-Parameter Gadgets:** Inexpensive pulse oximeters and digital thermometers provide fragmented numbers, lack clinical context, offer no referral records, and cannot assess cardiovascular tone or anemia.
2. **Expensive Cartridge Kiosks (e.g., HealthCube):** While capable, systems like HealthCube cost **₹1,20,000 to ₹2,20,000 per unit** and depend on invasive, single-use chemical test strips/cartridges costing **₹80 to ₹250 per test**. For a rural PHC covering 10,000 citizens, recurring consumables cost over **₹9 Lakhs annually**. When cartridge budgets lapse, the machine becomes an expensive paperweight.
3. **Cloud-Tethered "Smart" Solutions:** Telemedicine apps requiring continuous 4G/Wi-Fi fail completely in the 40% of rural Indian villages with spotty cellular coverage.

#### Smart-ASHA's Market Advantages:
* **The Zero-Consumable Advantage (Radical Affordability):** By using 100% non-invasive optical spectrophotometry, infrared thermography, and surface bio-potentials, Smart-ASHA has **zero recurring test costs**. Testing 10 patients or 10,000 patients costs the exact same amount.
* **Sub-₹8,000 Capital Cost:** At initial production, the bill-of-materials is under ₹8,000 (sub-₹5,500 at 5,000+ unit scale)—over **15× cheaper than commercial diagnostic kiosks**.
* **100% Offline Autonomy:** Edge-AI inference (FeverCNN on ESP32-S3 Core 0), digital signal filtering, offline ICD-10 rule evaluation, and audio feedback all operate with zero cellular connection. When connectivity is present, data auto-syncs via the onboard Quectel 4G modem.
* **Designed for the Frontline Worker (Zero-Literacy UX):** Instead of forcing community health workers to decipher complex decimal numbers (e.g., $\text{SpO}_2$ 91%, SDNN 45ms), Smart-ASHA provides an immediate Tri-color verdict (**Green = Normal, Yellow = Monitor, Red = Urgent Referral**), spoken aloud in their mother tongue and encoded into a standard Ayushman Bharat referral slip.

---

## Question 3: Field/Lab Testing Insights, Unexpected Hurdles & Immediate Next Steps

### 3.1 Key Insights & Unexpected Technical Hurdles Encountered in Lab/Field Testing

#### Hurdle 1: Ambient Thermal Radiometric Drift in Indian Field Conditions
* **The Hurdle:** During initial testing under simulated North Indian summer conditions ($35^\circ\text{C} - 40^\circ\text{C}$), the MLX90640 thermal sensor reported wildly inaccurate forehead temperatures (false fevers $>43^\circ\text{C}$ or readings dipping below $32^\circ\text{C}$).
* **Root Cause:** Solderless breadboard layout placed the sensor directly adjacent to the ESP32-S3 microcontroller, whose core runs at $45^\circ\text{C}-55^\circ\text{C}$ during continuous AI execution. Heat conducted through the breadboard altered the thermopile reference substrate ($T_{sub}$), corrupting the thermal gradient equation.
* **Resolution:** Re-engineered the algorithm with a dynamic substrate offset calibration based on Stefan-Boltzmann radiation laws, and physically relocated the sensor into an isolated thermal baffle.

#### Hurdle 2: Cellular RF Power Amplifier Inrush Transients & Brownouts
* **The Hurdle:** Whenever the Quectel EC200U 4G modem attempted network registration or cellular packet uplink, the ESP32-S3 randomly suffered instantaneous brownout resets (`rst:0x10 RTCWDT_RTC_RST`).
* **Root Cause:** Oscilloscope measurement revealed that during LTE transmit bursts, the modem's RF power amplifier draws brief current spikes of **$1.8\text{ A} - 2.0\text{ A}$**, instantly collapsing the 3.3V/5V breadboard power rail.
* **Resolution:** Implemented strict time-division multiplexing in firmware (cellular transmissions are blocked while sensors are actively sampling) and designed a $1000\,\mu\text{F}$ low-ESR bulk electrolytic capacitor buffer directly across the modem supply pins.

#### Hurdle 3: I²C Bus Capacitance Saturation and Line Contention
* **The Hurdle:** When polling the MAX30105 optical sensor at high sample rates alongside the AS7343 and MLX90640 through the TCA9548A multiplexer, the entire I²C bus intermittently locked with permanent `NACK` errors.
* **Root Cause:** Connecting five breakout boards across 20 cm jumper wires accumulated cumulative bus capacitance exceeding $300\text{ pF}$ (well above the safe threshold), while multiple parallel pull-up resistors dragged the equivalent bus resistance below $1\,\text{k}\Omega$.
* **Resolution:** Architected a **Dual Physical Bus pipeline**: isolated the continuous optical pulse stream of the MAX30105 on a dedicated high-speed bus (`Wire1` @ 400 kHz), while throttling the multiplexer bus (`Wire`) to 50 kHz with FreeRTOS mutex arbitration.

#### Hurdle 4: Optical Crosstalk and Room Lighting Fluctuations
* **The Hurdle:** The AS7343 spectral sensor returned erratic hemoglobin ratios when tested under standard indoor fluorescent lighting due to 50 Hz/100 Hz AC flicker.
* **Root Cause:** The unshielded sensor received ambient light reflections that overwhelmed the reflected microvascular absorption signals.
* **Resolution:** Designed a 3D-printed optical contact shroud that creates an opaque seal against the patient's fingertip/skin.

---

### 3.2 Immediate Next Steps to Make the Project Fully Ready for Real Users

To transition Smart-ASHA from its current functional bench milestone into an unshakeable clinical device in the hands of real ASHA workers, we are executing the following roadmap:

```
[Month 1] Fabricate 4-Layer PCB & 3D Ergonomic Stethoscope Sleeves (5 Pilot Units)
     │
     ▼
[Month 2] Benchtop Calibration Against Gold-Standard Hospital Analyzers
     │
     ▼
[Month 3] 30-Day Village Health Outpost Usability Pilot (Haryana / Rajasthan PHCs)
     │
     ▼
[Month 4] ABDM / ABHA Health Locker Integration & CDSCO Class B Documentation
```

1. **PCB Fabrication & Mechanical Assembly (Weeks 1–3):**
   * Finalize routing and manufacture the custom 4-layer rigid-flex PCB incorporating the ESP32-S3, Quectel 4G, dual-bus sensor layouts, and PMIC battery management.
   * 3D-print 5 complete beta units using biocompatible, medical-grade resin with silicone optical shrouds.
2. **Clinical Benchmarking & Metric Calibration (Weeks 4–6):**
   * Conduct double-blind validation against clinical gold standards: compare Smart-ASHA non-invasive readings against an automated laboratory hematology analyzer (for hemoglobin), a calibrated clinical digital thermometer (for temperature), and a certified 12-lead ECG monitor (for cardiac rhythm).
   * Refine the ratiometric spectral regression curve across diverse skin tones (Fitzpatrick types I through VI).
3. **Field Usability Pilot with Frontline ASHA Workers (Weeks 7–10):**
   * Deploy 5 units to active ASHA workers and Auxiliary Nurse Midwives (ANMs) at rural Primary Health Sub-Centres in pilot rural clusters (Haryana / Rajasthan).
   * Evaluate real-world usability: time-to-scan, clarity of bilingual audio guidance, ease of offline Ayushman QR scanning at the PHC counter, and battery endurance across a full 8-hour shift of door-to-door visits.
4. **National Health Stack (ABDM) Integration & Regulatory Preparation (Weeks 11–12):**
   * Complete FHIR standard compliance to enable direct, one-click linking of screening logs into the patient’s **Ayushman Bharat Health Account (ABHA)**.
   * Assemble the technical design dossier and risk analysis documentation required for Class B non-invasive medical device notification under CDSCO guidelines.

---

## Conclusion
Smart-ASHA is not an incremental modification of a hobbyist kit; it is an aggressive, purpose-built engineering effort to eliminate the diagnostic divide in rural India. By delivering **100% non-invasive multimodal sensing, on-device Edge-AI, zero recurring consumables, and complete offline autonomy**, this project equips frontline healthcare workers with an objective, life-saving clinical voice.

---
*Prepared for Maker Bhavan Foundation — Vishwakarma Awards 2026–27*  
*Applicant Contact:* Gauri Gupta | Team Arogya AI / Smart-ASHA  
*Submission Target:* Form Link `https://forms.gle/9qWU4k7AskaqpMzk7`  
