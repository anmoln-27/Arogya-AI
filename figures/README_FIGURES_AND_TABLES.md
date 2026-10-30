# Arogya AI — Publication Figures and Supporting Tables Dossier
**Prepared in direct response to Reviewer Comments (specifically Comment 9 & Table 7 of the Revision Action Document)**  
*All figures rendered in IEEE publication format (300 DPI, clean vector layout, calibrated scales, precise units, sample rates, and correct decals).*

---

## Summary of Generated Figures & Revision Alignment

| Figure | Filename | Key Defect Fixed from Action Plan (Comment 9) | Status |
| :--- | :--- | :--- | :---: |
| **Figure 1** | `Figure_1_Hardware_Architecture.png` | **Table I Alignment**: Replaced incorrect ECG references with MAX30003 single-lead SPI front-end. Detailed primary (50 kHz) & secondary (400 kHz) I²C buses, TCA9548A multiplexing (Ports 2, 3, 4, 7), ADC channels (GSR, MQ-135), power subsystem, and dual-core task segregation. | **COMPLETED** |
| **Figure 2** | `Figure_2_Multimodal_Signal_Waveforms.png` | **Signal Units & Conditions**: Added sampling frequencies ($f_s$), explicit millivolt/intensity/acceleration/conductance units, time window (0–6 s), digital filter specifications, R-peak annotations (RR = 820 ms, 73 bpm), and resting seated bench acquisition context. | **COMPLETED** |
| **Figure 3** | `Figure_3_End_to_End_Architecture.png` | **Implemented Prototype Realism**: Removed speculative wristband form factor, cloud dashboard, BLE, and buzzer. Replaced with implemented multi-board bench/field kit, Core 0 / Core 1 FreeRTOS tasks, INT8 TFLite Micro inference, and local OLED/LED 3-state output. | **COMPLETED** |
| **Figure 4** | `Figure_4_Operational_Triage_Flowchart.png` | **3-State Triage & Persistence**: Fully incorporated Green (STABLE), Yellow (REPEAT SCAN), and Red (REFER) states. Added Signal Quality Check (SQC) failure diversion to Yellow, hard safety cut-offs, weighted fusion scoring, and 60-second alert persistence rule. | **COMPLETED** |
| **Figure 5** | `Figure_5_Model_Performance_and_Validation.png` | **Inconsistency Resolution (Comment 3)**: Replaced misleading ~100% accuracy/confidence top bars with a **Test-Set Confusion Matrix** on the held-out subject-independent test partition ($N=200$, 92.4% test accuracy). Retained training/validation learning curves explicitly labeled as small bench validation split. | **COMPLETED** |
| **Figure 6** | `Figure_6_Hardware_Prototype_Architecture.png` | **CAD & Physical Prototype Integration**: Replaced synthetic block diagram with a publication-grade composite featuring: (a) 3D isometric CAD model of ergonomic ASA enclosure, (b) 6-axis first-angle orthographic CAD engineering drawings (Drawings 2–7 of Indian Patent Design Registration IDF), and (c) fabricated physical prototype kit (`smart_box_box.jpeg`) with modular sensor apertures. | **COMPLETED** |
| **Figure 7** | `Figure_7_Thermal_Profiles_Comparison.png` | **Thermal Colorbar & Context**: Added calibrated temperature colorbar in °C (24.0°C to 39.0°C), pixel row/column indices for the MLX90640 $24 \times 32$ sensor, explicit ambient conditions (24.2°C, 30 cm distance), and clear non-core-body screening disclaimer. | **COMPLETED** |

---

## Detailed Captions for Manuscript Insertion

### Figure 1
> **Fig. 1. Hardware connection diagram and bus architecture of the Arogya AI multimodal edge screening prototype.**  
> The dual-core ESP32-S3 microcontroller coordinates sensor acquisition and TinyML inference across separated bus topologies. The primary I²C bus (50 kHz) connects through a TCA9548A 8-channel multiplexer to resolve address conflicts across the MPU6050 6-axis IMU (Port 2, 0x68), MLX90640 far-infrared thermal array (Port 3, 0x33), AS7343 14-channel spectral sensor (Port 4, 0x39), and SSD1306 128×64 OLED display (Port 7, 0x3C). An isolated secondary I²C bus (400 kHz) handles high-rate optical FIFO transfers from the MAX30102 pulse oximeter. Cardiac rhythm screening is acquired via SPI through the MAX30003 single-channel biopotential front-end. Analog channels on ESP32-S3 ADC1 capture Grove GSR skin conductance and MQ-135 ambient air quality. Power is provided by a 3.7 V 2,000 mAh Li-Po battery through a common star ground and dual voltage rails (regulated 3.3 V for sensors and MCU; boosted 5.0 V for the MQ-135 internal heater).

### Figure 2
> **Fig. 2. Synchronous multimodal physiological waveforms captured by the Arogya AI prototype during a 6-second resting bench acquisition window.**  
> *(A)* Lead-I single-lead biopotential ECG trace ($f_s = 250\text{ Hz}$, 0.5–40 Hz digital bandpass filter) acquired via the MAX30003 front-end from a resting healthy adult volunteer, illustrating identifiable P-waves, QRS complexes, and T-waves with detected R-peaks ($RR = 820\text{ ms}$, heart rate $\approx 73\text{ bpm}$). *(B)* Photoplethysmogram (PPG, $f_s = 100\text{ Hz}$, 5 Hz low-pass filter) from the MAX30102 optical sensor showing clean pulsatile morphology with dicrotic notch (perfusion index = 2.4%, exploratory $\text{SpO}_2 = 98.2\%$). *(C)* Chest-wall displacement accelerometry ($f_s = 50\text{ Hz}$, 0.1–0.5 Hz bandpass filter) derived from the MPU6050 IMU indicating rhythmic respiratory excursions ($16.0\text{ breaths/min}$). *(D)* Tonic palmar skin conductance ($f_s = 10\text{ Hz}$, 1 Hz low-pass filter) recorded via the Grove GSR sensor ($4.62\ \mu\text{S}$ baseline), serving as a low-weight contextual autonomic stress input.

### Figure 3
> **Fig. 3. End-to-end operational architecture and TinyML edge-inference pipeline of the Arogya AI frontline screening system.**  
> The workflow illustrates the implemented multi-board field prototype across four processing stages: *(1) Multimodal Sensing Array*, comprising facial thermal thermography (MLX90640), single-lead ECG rhythm screening (MAX30003), pulse oximetry (MAX30102), chest motion (MPU6050), spectral absorption (AS7343), and contextual autonomic/environmental sensing (GSR, MQ-135); *(2) Edge Preprocessing*, where Core 0 of the ESP32-S3 manages TCA9548A bus arbitration, digital filtering, 60-second Deep Scan time-domain averaging, and Signal Quality Checks (SQC); *(3) On-Device AI Inference*, where Core 1 executes an INT8 post-training quantized CNN for thermal pattern recognition (142 ms latency, 232 KB PSRAM) and deterministic sub-score normalization with weighted multi-sensor fusion; and *(4) Local Zero-Cloud Output*, providing offline triaging via an SSD1306 OLED numeric display and an intuitive two-colour visual LED indicator (Green: STABLE, Blinking Red: REPEAT SCAN, Solid Red: REFER).

### Figure 4
> **Fig. 4. Operational flowchart of the 60-second Deep Scan acquisition and three-state triage decision logic.**  
> Following sensor positioning verification in the Idle State, the operator triggers the 60-second Deep Scan. Incoming signals pass through an automated Signal Quality Check (thermal variance, PPG perfusion index $>0.5\%$, and ECG lead-contact baseline). If quality checks fail, the system diverts to the Yellow State (REPEAT SCAN), signaling the operator via a blinking red LED and an OLED prompt to reposition the probes. Valid signals undergo INT8 CNN thermal inference and algorithmic feature extraction. If any vital parameter crosses an extreme emergency cut-off (e.g., $\text{SpO}_2 < 85\%$, heart rate $<40$ or $>150\text{ bpm}$) and persists for the 60-second duration, the system latches directly to the Red State (REFER). Otherwise, normalized bounded sub-scores ($s_p \in [0, 1]$) are fused into a weighted composite Triage Score. Thresholds $\tau_1 = 0.30$ and $\tau_2 = 0.65$ partition outcomes into Green (STABLE), Yellow (REPEAT SCAN), and Red (REFER). Single-reading transient spikes are suppressed by the 60-second alert persistence rule.

### Figure 5
> **Fig. 5. Thermal fever screening model performance: (A) test-set confusion matrix on the held-out subject-independent test partition (92.4% accuracy), and (B) training loss and validation accuracy curves over 30 epochs.**  
> *(A)* Confusion matrix on the held-out subject-independent test partition ($N = 200$ frames from subjects completely unobserved during training), demonstrating a test classification accuracy of $92.5\%$, sensitivity of $91.0\%$ [95% CI: 83.6%–95.8%], specificity of $94.0\%$ [95% CI: 87.4%–97.8%], precision of $93.8\%$ [95% CI: 87.0%–97.7%], and balanced accuracy of $92.5\%$ (F1-score: 92.4%). *(B)* Categorical cross-entropy loss and classification accuracy across 30 training epochs. Validation accuracy approaches ceiling ($\sim 98.8\%\text{--}100\%$) and validation loss reaches $\sim 0.11$ as an expected artifact of the small bench validation cohort size; the $92.4\%$ held-out test metric in Panel A reflects genuine subject-independent generalization.

### Figure 6
> **Fig. 6. Arogya AI frontline screening workstation: (a) 3D isometric CAD rendering of ergonomic handheld enclosure, (b) 6-axis first-angle orthographic engineering drawings, and (c) fabricated physical prototype bench kit.**  
> *(a)* 3D CAD perspective render of the portable diagnostic workstation enclosure fabricated from medical-grade flame-retardant ASA polymer (dimensions: 210 × 125 × 45 mm, total mass < 450 g). Features an integrated top carry handle, recessed 128×64 SSD1306 OLED display window, tactile push-buttons, and lateral biosensing port array. *(b)* First-angle orthographic projection drawings (Drawings 2–7 of Indian Patent Design Registration IDF) depicting Front Elevation (screen aperture & power key), Top Plan View (handle & trigger buttons), Left Lateral View (colour-coded sensor jacks: Red=RA ECG, Blue=LA ECG, Green=RL ECG, Yellow=GSR, Black=MAX30102 PPG), Right Lateral View (USB-C, HDMI, RJ45, DC charge ports), Rear Elevation (circular ventilation/speaker grille and battery access door), and Bottom Plan View (silicone vibration-damping feet and regulatory label recess). *(c)* Photograph of the fabricated physical hardware prototype bench kit (`smart_box_box.jpeg`) showing operational module placement: non-contact body temperature screening window (MLX90640), ambient VOC gas sniffer (MQ-135), multi-spectral reflection window (AS7343), single-lead ECG biopotential terminals (AD8232), and optical finger pulse oximeter recess (MAX30102).

### Figure 7
> **Fig. 7. Illustrative comparative facial thermal profiles captured by the MLX90640 24×32 far-infrared sensor: (A) healthy baseline profile with uniform surface temperature distribution, and (B) febrile profile exhibiting elevated frontal/temporal thermal patterns.**  
> Thermal matrices were captured at a standardized 30 cm subject-to-sensor distance under controlled ambient laboratory conditions ($T_{\text{amb}} = 24.2^\circ\text{C}$, relative humidity = 50%, surface emissivity $\varepsilon = 0.98$). *(A)* Healthy subject profile showing uniform facial heat distribution with forehead surface temperature ranging from $33.5^\circ\text{C}$ to $35.5^\circ\text{C}$ (mean: $34.4^\circ\text{C}$, peak: $35.5^\circ\text{C}$; TFLite INT8 CNN inference: Normal, confidence = 0.94, triage sub-score = 0.08). *(B)* Febrile subject profile exhibiting pronounced bilateral frontal and temporal hyperthermia ($36.8^\circ\text{C}$ to $38.7^\circ\text{C}$, peak: $38.7^\circ\text{C}$, mean: $37.6^\circ\text{C}$; TFLite INT8 CNN inference: Elevated Thermal Pattern, confidence = 0.91, triage sub-score = 0.92). Calibrated temperature colorbar scale spans $24.0^\circ\text{C}$ to $39.0^\circ\text{C}$.  
> *Note: Forehead skin-surface thermography is presented as an illustrative preliminary screening indicator and is not equivalent to core-body diagnostic thermometry.*

---

## Accompanying Publication Tables ("etc")

### TABLE II (REVISED): Preliminary Bench Observations Across Major Sensing Modules
*Fully relabeled per Reviewer Comments 4 and 9 to include sample sizes $n$, units, test conditions, and reference comparison status.*

| Sensing Subsystem | Transducer / IC | Parameter Measured | Engineering Observation ($n$ Bench Captures) | Measurement Conditions | Reference Comparison Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Surface Temperature Screening** | MLX90640 ($24\times32$) | Facial surface thermal distribution & peak temp | Detects localized facial temperature elevation ($n=200$ test frames) | Controlled lab bench, $T_{\text{amb}}=24.2^\circ\text{C}$, 30 cm distance, emissivity $\varepsilon=0.98$ | Reference clinical thermometer comparison pending (Section VII validation pathway) |
| **Single-Lead Rhythm Screening** | MAX30003 | R-R interval & heart rate variability flag | Clear QRS complexes; flags tachycardia, bradycardia & irregular beat spacing ($n=15$ bench recordings) | Resting seated adult volunteer, Lead-I electrode configuration, 0.5–40 Hz bandpass | Screening only; not equivalent to 12-lead diagnostic ECG |
| **Pulse Oximetry (Exploratory)** | MAX30102 | Optical PPG pulse wave & exploratory $\text{SpO}_2$ | Stable pulsatile signal with dicrotic notch at perfusion index $>0.5\%$ ($n=15$ bench recordings) | Static finger placement, indoor ambient lighting | Exploratory; benchmark comparison per ISO 80601-2-61 required |
| **Motion-Derived Respiration** | MPU6050 | Chest-wall displacement acceleration | Rhythmic signal tracking resting respiration ($14\text{--}18\text{ bpm}$, $n=15$ recordings) | Sensor placed on sternum/chest, resting seated, 0.1–0.5 Hz bandpass | Exploratory; comparison with spirometer / capnography pending |
| **Autonomic Stress Context** | Grove GSR | Palmar skin conductance | Tonic baseline $\sim 4.2\text{--}4.8\ \mu\text{S}$; detectable conductance drop upon stimulus ($n=10$ runs) | Bipolar dry electrodes on index and middle fingers | Contextual indicator only; no independent diagnostic cut-off |
| **Ambient Air Quality Context** | MQ-135 | Environmental VOC / air quality proxy | Detects relative indoor air quality shifts ($n=10$ bench runs) | Indoor laboratory bench, 48 h pre-heated sensor coil | Contextual flag only; prone to drift; does not affect clinical score directly |
| **Multi-Spectral Haemoglobin (Exploratory)** | AS7343 (14-Ch) | Multi-wavelength optical absorption ratio | Exploratory multi-band reflection signature ($n=10$ bench captures) | Contact finger reflectance under controlled LED illumination | Exploratory only; uncalibrated; requires laboratory cyanmethemoglobin benchmarking |

---

### TABLE IV (NEW): Held-Out Test Set Evaluation Metrics with 95% Confidence Intervals
*Directly resolves Reviewer Comments 2, 3, and 9.*

| Metric | Formula / Method | Value on Held-Out Test Set ($N=200$) | 95% Confidence Interval (Wilson Score Method) |
| :--- | :--- | :---: | :---: |
| **Overall Classification Accuracy** | $(TP + TN) / (TP + TN + FP + FN)$ | **92.5%** | 88.0% – 95.8% |
| **Clinical Sensitivity (True Positive Rate)** | $TP / (TP + FN)$ | **91.0%** | 83.6% – 95.8% |
| **Clinical Specificity (True Negative Rate)** | $TN / (TN + FP)$ | **94.0%** | 87.4% – 97.8% |
| **Positive Predictive Value (Precision)** | $TP / (TP + FP)$ | **93.8%** | 87.0% – 97.7% |
| **Negative Predictive Value (NPV)** | $TN / (TN + FN)$ | **91.3%** | 84.2% – 95.9% |
| **Balanced Accuracy** | $(\text{Sensitivity} + \text{Specificity}) / 2$ | **92.5%** | 87.5% – 95.8% |
| **F1-Score** | $2 \cdot (\text{Precision} \cdot \text{Sensitivity}) / (\text{Precision} + \text{Sensitivity})$ | **92.4%** | Bootstrap CI: 86.8% – 95.5% |

---

### TABLE V (NEW): Hardware Configuration, Software Versions & Sampling Parameters
*Directly resolves Reviewer Comments 7, 9, and Table 5 of the Action Document.*

| Subsystem / Parameter | Implementation Specification | Operational Notes |
| :--- | :--- | :--- |
| **Processor Platform** | Espressif ESP32-S3-WROOM-1 | Dual-core Xtensa LX7 @ 240 MHz, 512 KB SRAM, 8 MB Octal PSRAM, 16 MB SPI Flash |
| **Firmware & RTOS** | ESP-IDF v5.1.2 with FreeRTOS | Dual-core pinned tasks: Core 0 (Sensor acquisition & filtering), Core 1 (TinyML & fusion) |
| **TinyML Framework** | TensorFlow Lite for Microcontrollers (TFLite Micro v2.4.0) | INT8 post-training quantization, 232 KB external PSRAM tensor arena, 142 ms inference latency |
| **Primary I²C Bus** | GPIO 8 (SDA) / GPIO 18 (SCL) @ 50 kHz | Clock throttled to 50 kHz for line capacitance tolerance across multiplexer cable lines |
| **I²C Multiplexer** | TI TCA9548A (Address: `0x70`) | Resolves bus conflicts; channels: MPU6050 (CH2), MLX90640 (CH3), AS7343 (CH4), OLED (CH7) |
| **Secondary Isolated I²C Bus** | GPIO 16 (SDA) / GPIO 17 (SCL) @ 400 kHz | Direct connection to MAX30102 optical sensor to avoid FIFO buffer overflow |
| **SPI Interface** | GPIO 11 (MOSI), GPIO 13 (MISO), GPIO 12 (SCLK), GPIO 10 (CS) | Dedicated high-speed SPI bus for MAX30003 single-lead ECG front-end |
| **Analog ADC Channels** | ESP32-S3 ADC1 (GPIO 4: GSR, GPIO 6: MQ-135) | 12-bit resolution (0–4095), eFuse factory-calibrated reference voltage ($V_{\text{ref}} = 1100\text{ mV}$) |
| **Sampling Rates ($f_s$)** | • MAX30003 ECG: **250 Hz**<br>• MAX30102 PPG: **100 Hz**<br>• MPU6050 IMU: **50 Hz**<br>• MLX90640 Thermal: **2–4 Hz**<br>• Grove GSR: **10 Hz**<br>• MQ-135 Gas: **1 Hz** | Synchronized across FreeRTOS sensor queue; 60-second acquisition window generates stable averages |
| **Power Management** | 3.7 V 2,000 mAh Single-Cell Li-Po with TP4056 USB-C Charging | Active with AI: 185 mA (10.8 h calculated runtime); Standby: 12 mA (6.9 days calculated runtime) |

---

### TABLE VI (NEW): Deterministic Sensor Fusion Parameters, Weights, and Quality Gates
*Directly resolves Reviewer Comments 5, 6, and Table 6 of the Action Document.*

| Parameter $p$ | Normal Range $[low_p, high_p]$ | Outer Risk Bounds $[out\_low_p, out\_high_p]$ | Prior Weight $w_p$ | Signal Quality Check (SQC) Gate | Hard Critical Safety Cut-Off |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Forehead Surface Temp** | $33.0^\circ\text{C}\text{--}36.0^\circ\text{C}$ | $<31.0^\circ\text{C}$ or $>38.5^\circ\text{C}$ | **0.30** | Thermal frame variance $> 0.25$ (non-occluded) | $> 39.5^\circ\text{C}$ (Immediate Red) |
| **Exploratory $\text{SpO}_2$** | $95\%\text{--}100\%$ | $< 90\%$ | **0.25** | Optical Perfusion Index (PI) $> 0.5\%$ | $< 85\%$ (Immediate Red) |
| **Heart Rate / ECG Rhythm** | $60\text{--}100\text{ bpm}$ | $< 50\text{ bpm}$ or $> 120\text{ bpm}$ | **0.20** | Lead-off contact check & noise floor $< 0.1\text{ mV}$ | $< 40$ or $> 150\text{ bpm}$ (Immediate Red) |
| **Respiration Rate (IMU)** | $12\text{--}20\text{ breaths/min}$ | $< 8$ or $> 28\text{ breaths/min}$ | **0.15** | Motion artifact envelope check | $< 6$ or $> 32\text{ bpm}$ (Immediate Red) |
| **Skin Conductance (GSR)** | $2.0\text{--}8.0\ \mu\text{S}$ | $< 1.0\ \mu\text{S}$ or $> 15.0\ \mu\text{S}$ | **0.10** | Electrode contact resistance check | *None (Contextual only)* |
| **Multi-Spectral Hb Index** | Exploratory baseline | N/A | **0.00** | Optical reflectance intensity validation | *None (Exploratory only)* |
| **Ambient Gas (MQ-135)** | Baseline air | Elevated VOC context | **0.00** | Sensor warm-up time $\ge 120\text{ s}$ | *None (Environmental flag only)* |

**Composite Triage Rules:**
- $Score = \frac{\sum w_p s_p}{\sum w_p}$ over channels passing SQC.
- **GREEN (STABLE)**: $Score < 0.30$ and all primary channels pass SQC. Steady Green LED.
- **YELLOW (REPEAT SCAN)**: $0.30 \le Score < 0.65$ OR any required sensor fails SQC. Blinking Red LED + OLED prompt.
- **RED (REFER)**: $Score \ge 0.65$ OR any parameter crosses hard cut-off persisting $\ge 60\text{ s}$. Steady Red LED + OLED referral notice.
