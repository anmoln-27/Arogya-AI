# 🔬 Smart-ASHA: Hardware Limitations & Environmental Post-Mortem

**Reference Document:** `Limitations.pdf`  
**Scope:** Physical, electrical, and environmental constraints encountered during breadboard prototyping of the Smart-ASHA diagnostic kit.

---

## 1. Power Rail Sag & Current Starvation

### The Problem
During cold boot or concurrent sensor sampling, the ESP32-S3 intermittently reset with brownout notifications:
```text
rst:0x10 (RTCWDT_RTC_RST) or rst:0xc (RTC_SW_CPU_RST)
```
The OLED screen occasionally dimmed or locked during thermal camera acquisition.

### Electrical Analysis
The total dynamic power budget of the prototype exceeded the current delivery limit of the onboard 3.3V Low-Dropout (LDO) regulator when powered via a standard laptop USB 2.0 port ($500\text{ mA}$ limit):

| Component | Current Demand | Behavior |
|:---|:---|:---|
| **ESP32-S3** | $240\text{ mA} - 310\text{ mA}$ | Dual-core active + vector processing peak spikes |
| **Quectel EC200U-CN (4G Modem)** | **$500\text{ mA}$ avg, $1.8\text{ A} - 2.0\text{ A}$ peak** | High-energy RF power amplifier bursts during LTE network attach and uplink transmissions |
| **MLX90640 Thermal Sensor** | $23\text{ mA}$ continuous | Internal capacitor charging transients |
| **MAX30105 Optical Sensor** | $\approx 12.5\text{ mA}$ per LED | High-power LED pulse bursts (`0x3F`) at high sample rates |
| **AS7343 Spectral Sensor** | $15\text{ mA} - 20\text{ mA}$ | Active analog integration and photodiode arrays |
| **SH1106 1.3" OLED** | $25\text{ mA} - 40\text{ mA}$ | Highly dependent on active pixel fill factor |

> [!WARNING]
> **4G LTE Cellular Transmission Inrush Hazard:**  
> The 7Semi board integrates a Quectel EC200U-CN 4G LTE modem. During network registration or cellular data packet bursts, the modem's RF power amplifier draws brief current spikes up to **$2.0\text{ A}$**. If the prototype is powered solely from a standard laptop USB 2.0 port ($500\text{ mA}$ limit) or an under-rated USB hub, these bursts will instantly collapse the $5\text{V}/3.3\text{V}$ rail, triggering immediate microcontroller brownout reboots (`RTCWDT_RTC_RST`).

### Physical Mitigation
1. **Bulk Capacitive Buffering for Cellular Transients:** Added a **$470\,\mu\text{F} - 1000\,\mu\text{F}$ low-ESR capacitor** directly across the modem power rail, coupled with a **$100\,\mu\text{F} + 0.1\,\mu\text{F}$ ceramic capacitor** pair across the primary 3.3V and GND breadboard rails to swallow transient dropouts.
2. **External 5V / 2A+ Power Supply or LiPo:** When testing 4G transmission, power must be supplied via a dedicated $5\text{V}/2\text{A}$ wall adapter or a $3.7\text{V}$ LiPo battery (18650 cell with $\ge 2\text{C}$ discharge capability) connected to the 7Semi board's battery input.
3. **Dedicated LDO Allocation & Time-Division Scheduling:** Shifted high-drain optical emitters to dedicated voltage regulation. In firmware, schedule cellular data transmission **after** sensor acquisition completes, never simultaneously during high-current thermal sensor reads.

---

## 2. Thermal Camera Radiometric Drift (Delhi Ambient Environment)

### The Problem
In testing environments with high ambient room temperatures ($>35^\circ\text{C}$ to $40^\circ\text{C}$, typical of Delhi summer field conditions), the MLX90640 raw pixel readings drifted significantly, reporting forehead temperatures above $44^\circ\text{C}$ or falling below $32^\circ\text{C}$ inside enclosed prototype housings.

### Physical Root Causes
1. **Self-Heating of the Sensor Substrate:** The MLX90640 relies on thermopile elements measuring the temperature difference between the target object and the sensor silicon substrate:
   $$V_{IR} \propto (T_{obj}^4 - T_{sub}^4)$$
   When placed in close proximity to the ESP32-S3 ($>50^\circ\text{C}$ under AI load), heat transferred through jumper wires and shared air space raised $T_{sub}$, corrupting the internal gradient compensation.
2. **Enclosure Heat Trapping:** Without forced ventilation, heat from the display controller and microcontroller built up around the lens.

### Engineering Compensation
* **Dynamic / Experimental Offset Calibration:** Implemented an experimental offset calibration factor (`boxOffset = -9.8` to `-3.5` depending on enclosure draft).
* **60-Second High-Watermark Peak Extraction Algorithm:** Rather than relying on instantaneous single-frame reads, the system tracks the maximum valid pixel temperature over the duration of the scan, filtering out transient thermal blips.

---

## 3. Breadboard Parasitic Capacitance & I²C Bus Integrity

### The Problem
Sensors intermittently failed communication with `NACK` errors, and the AS7343 repeatedly returned static `1` readings across all 18 channels.

### Electrical Root Causes
1. **Bus Line Capacitance ($C_b$):** Connecting five separate I²C boards (TCA9548A, MLX90640, AS7343, MPU6050, SH1106) across long DuPont breadboard jumpers created a cumulative bus capacitance well in excess of the $400\text{ pF}$ I²C specification limit ($C_b > 300\text{ pF}$).
2. **Conflicting Onboard Pull-ups:** Each breakout module (Adafruit, SparkFun) included its own onboard $4.7\,\text{k}\Omega$ or $10\,\text{k}\Omega$ pull-up resistors to 3.3V. Operating in parallel through the multiplexer reduced the equivalent pull-up resistance ($R_p$) below $1\,\text{k}\Omega$, pulling excessive sink current and distorting logic low ($V_{IL}$) levels.

### Physical Resolution
1. **Bus Segregation (Dual Physical Buses):** Moved the high-speed MAX30105 sensor completely off the shared bus onto an independent physical bus (`Wire1`: GPIO 16/17), freeing the multiplexer from handling continuous optical streaming.
2. **Frequency Reduction:** Reduced the primary I²C bus clock to **$50\text{ kHz}$** to allow the slow rise times caused by jumper wire capacitance to safely reach valid logic-high thresholds ($V_{IH} \ge 0.7 \times V_{DD}$).

---

## 4. Optical Isolation & Motion Artifacts

### Limitations Identified in Prototype
1. **Spectral Sensor Optical Leakage:** The AS7343 requires controlled reflected light. On the open breadboard, ambient room lighting (fluorescent and LED flickering at 50 Hz / 100 Hz) overpowered the reflected optical signal from human tissue.
2. **MAX30105 Motion Sensitivity:** Solderless breadboard jumper flex during physical finger contact introduced movement artifacts into the PPG signal, corrupting pulse wave intervals.
3. **AD8232 ECG Noise Coupling:** The single-lead ECG signal path picked up significant 50 Hz electromagnetic interference from nearby laptop chargers and USB power bricks, necessitating careful shielding and ADC filtering.

---

## 5. Transition to Production (Prototype vs. Final Sleeve)

| Parameter | Breadboard Prototype (Current) | Production Stethoscope Sleeve (Target) |
|:---|:---|:---|
| **Interconnects** | 20cm jumper wires ($C_b > 300\text{ pF}$) | 4-layer rigid-flex PCB with controlled impedance |
| **I²C Clock** | Throttled to 50 kHz | Full 400 kHz Fast-Mode |
| **Thermal Isolation** | Open air near hot ESP32-S3 | Thermally isolated front baffle with silicone gasket |
| **Optical Path** | Open to ambient room light | Enclosed optical chamber with direct skin contact |
| **Power Supply** | USB VBUS through linear regulator | Dedicated low-noise LDO + LiPo battery management |
