import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
from PIL import Image

INPUT_DOCX = "Smart Asha Arogya AI updated paper (1)_original_backup.docx"
OUTPUT_DOCX_CORRECTED = "Smart Asha Arogya AI updated paper (corrected).docx"
OUTPUT_DOCX_UPDATED = "Smart Asha Arogya AI updated paper (1).docx"
FIGURES_DIR = os.path.abspath("figures")

NS = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}
W_NS = "http://purl.oclc.org/ooxml/wordprocessingml/main"

def qn(tag):
    return f"{{{W_NS}}}{tag}"

def create_element(name):
    return ET.Element(qn(name))

def create_run(text, bold=False, italic=False, size_pt=10, font_name="Times New Roman", highlight="yellow"):
    r = create_element("r")
    rPr = create_element("rPr")
    
    rFonts = create_element("rFonts")
    rFonts.attrib[qn("ascii")] = font_name
    rFonts.attrib[qn("hAnsi")] = font_name
    rPr.append(rFonts)
    
    if bold:
        rPr.append(create_element("b"))
    if italic:
        rPr.append(create_element("i"))
        
    sz = create_element("sz")
    sz.attrib[qn("val")] = str(int(size_pt * 2))
    rPr.append(sz)
    
    if highlight:
        hl = create_element("highlight")
        hl.attrib[qn("val")] = highlight
        rPr.append(hl)
        
    r.append(rPr)
    t = create_element("t")
    t.attrib["{http://www.w3.org/XML/1998/namespace}space"] = "preserve"
    t.text = text
    r.append(t)
    return r

def highlight_all_runs_in_element(element, color="yellow"):
    for r in element.findall(".//w:r", NS):
        rPr = r.find(qn("rPr"))
        if rPr is None:
            rPr = ET.Element(qn("rPr"))
            r.insert(0, rPr)
        hl = rPr.find(qn("highlight"))
        if hl is None:
            hl = ET.SubElement(rPr, qn("highlight"))
        hl.attrib[qn("val")] = color

def get_p_text(p):
    return "".join([t.text for t in p.findall(".//w:t", NS) if t.text])

def set_p_text(p, new_text, bold_prefix=None, font_size=10, highlight="yellow"):
    for child in list(p):
        if child.tag == qn("r"):
            p.remove(child)
            
    if bold_prefix and new_text.startswith(bold_prefix):
        p.append(create_run(bold_prefix, bold=True, size_pt=font_size, highlight=highlight))
        rest = new_text[len(bold_prefix):]
        p.append(create_run(rest, bold=False, size_pt=font_size, highlight=highlight))
    else:
        p.append(create_run(new_text, bold=False, size_pt=font_size, highlight=highlight))

def replace_in_p(p, old_str, new_str, highlight="yellow"):
    p_text = get_p_text(p)
    if old_str in p_text:
        # Check if old_str is cleanly inside one run
        replaced = False
        for r in p.findall(".//w:r", NS):
            t = r.find("w:t", NS)
            if t is not None and t.text and old_str in t.text:
                t.text = t.text.replace(old_str, new_str)
                rPr = r.find(qn("rPr"))
                if rPr is None:
                    rPr = ET.Element(qn("rPr"))
                    r.insert(0, rPr)
                hl = rPr.find(qn("highlight"))
                if hl is None:
                    hl = ET.SubElement(rPr, qn("highlight"))
                hl.attrib[qn("val")] = highlight
                replaced = True
                
        if not replaced:
            # Fallback for cross-run string splits: replace in full text and reconstruct
            new_full = p_text.replace(old_str, new_str)
            set_p_text(p, new_full, highlight=highlight)
        return True
    return False

def build_table(headers, data, title_text=None, highlight="yellow"):
    tbl = create_element("tbl")
    tblPr = create_element("tblPr")
    tblStyle = create_element("tblStyle")
    tblStyle.attrib[qn("val")] = "TableGrid"
    tblPr.append(tblStyle)
    tblW = create_element("tblW")
    tblW.attrib[qn("w")] = "0"
    tblW.attrib[qn("type")] = "auto"
    tblPr.append(tblW)
    jc = create_element("jc")
    jc.attrib[qn("val")] = "center"
    tblPr.append(jc)
    tbl.append(tblPr)
    
    # Header Row
    tr_h = create_element("tr")
    trPr_h = create_element("trPr")
    trPr_h.append(create_element("tblHeader"))
    tr_h.append(trPr_h)
    
    for h in headers:
        tc = create_element("tc")
        tcPr = create_element("tcPr")
        shd = create_element("shd")
        shd.attrib[qn("val")] = "clear"
        shd.attrib[qn("color")] = "auto"
        shd.attrib[qn("fill")] = "EAECEE"
        tcPr.append(shd)
        tc.append(tcPr)
        
        p = create_element("p")
        pPr = create_element("pPr")
        p_jc = create_element("jc")
        p_jc.attrib[qn("val")] = "center"
        pPr.append(p_jc)
        p.append(pPr)
        p.append(create_run(h, bold=True, size_pt=8, highlight=highlight))
        tc.append(p)
        tr_h.append(tc)
    tbl.append(tr_h)
    
    for row_data in data:
        tr = create_element("tr")
        for ci, cell_text in enumerate(row_data):
            tc = create_element("tc")
            p = create_element("p")
            pPr = create_element("pPr")
            p_jc = create_element("jc")
            p_jc.attrib[qn("val")] = "center" if ci in [2, 3] else "left"
            pPr.append(p_jc)
            p.append(pPr)
            is_bold = ci == 0 or cell_text.startswith("**")
            clean_text = cell_text.replace("**", "")
            p.append(create_run(clean_text, bold=is_bold, size_pt=8, highlight=highlight))
            tc.append(p)
            tr.append(tc)
        tbl.append(tr)
    return tbl

def update_drawing_dimensions_and_formatting(root, rels_root, figures_dir):
    rId_map = {}
    for rel in rels_root.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
        rId_map[rel.attrib.get("Id")] = rel.attrib.get("Target")

    image_to_fig = {
        "image1.png": "Figure_1_Hardware_Architecture.png",
        "image2.png": "Figure_2_Multimodal_Signal_Waveforms.png",
        "image3.png": "Figure_3_End_to_End_Architecture.png",
        "image4.png": "Figure_4_Operational_Triage_Flowchart.png",
        "image5.png": "Figure_5_Model_Performance_and_Validation.png",
        "image6.png": "Figure_6_Hardware_Prototype_Architecture.png",
        "image7.png": "Figure_7_Thermal_Profiles_Comparison.png",
    }

    drawings = root.findall(".//w:drawing", NS)
    print(f"Auditing and formatting {len(drawings)} drawings...")
    
    for i, d in enumerate(drawings):
        embed_id = None
        for b in d.iter():
            if b.tag.endswith("blip"):
                embed_id = b.attrib.get("{http://purl.oclc.org/ooxml/officeDocument/relationships}embed")
                if not embed_id:
                    embed_id = b.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        
        target_media = rId_map.get(embed_id, "")
        target_filename = os.path.basename(target_media)
        fig_name = image_to_fig.get(target_filename)
        
        if fig_name:
            fig_path = os.path.join(figures_dir, fig_name)
            if os.path.exists(fig_path):
                im = Image.open(fig_path)
                w_px, h_px = im.size
                aspect = w_px / h_px
                
                # Single column: 3.377 in = 3,089,910 EMUs. Full width: 6.50 in = 5,943,600 EMUs.
                cx = 5943600 # Full-page width (6.50 in) for crystal-clear readability
                cy = int(round(cx * h_px / w_px))
                
                print(f"  Drawing {i} ({fig_name}): {w_px}x{h_px} (aspect={aspect:.3f}) -> cx={cx} ({cx/914400:.2f} in), cy={cy} ({cy/914400:.2f} in)")
                
                for elem in d.iter():
                    if elem.tag.endswith("extent") or elem.tag.endswith("ext"):
                        if "cx" in elem.attrib and "cy" in elem.attrib:
                            elem.attrib["cx"] = str(cx)
                            elem.attrib["cy"] = str(cy)
                            
        # Format the parent paragraph
        for p in root.findall(".//w:p", NS):
            if d in list(p.iter()):
                pPr = p.find(qn("pPr"))
                if pPr is None:
                    pPr = ET.Element(qn("pPr"))
                    p.insert(0, pPr)
                
                jc = pPr.find(qn("jc"))
                if jc is None:
                    jc = ET.SubElement(pPr, qn("jc"))
                jc.attrib[qn("val")] = "center"
                
                ind = pPr.find(qn("ind"))
                if ind is not None:
                    pPr.remove(ind)
                ind = ET.SubElement(pPr, qn("ind"))
                ind.attrib[qn("left")] = "0"
                ind.attrib[qn("right")] = "0"
                ind.attrib[qn("firstLine")] = "0"
                
                sp = pPr.find(qn("spacing"))
                if sp is None:
                    sp = ET.SubElement(pPr, qn("spacing"))
                sp.attrib[qn("lineRule")] = "auto"
                sp.attrib[qn("line")] = "240"
                sp.attrib[qn("before")] = "120"
                sp.attrib[qn("after")] = "120"
                break

    # Format all figure caption paragraphs (Center, zero indent, clean spacing)
    for p in root.findall(".//w:p", NS):
        txt = get_p_text(p).strip()
        if txt.startswith("Figure ") or txt.startswith("Fig. ") or txt.startswith("FIGURE "):
            pPr = p.find(qn("pPr"))
            if pPr is None:
                pPr = ET.Element(qn("pPr"))
                p.insert(0, pPr)
            jc = pPr.find(qn("jc"))
            if jc is None:
                jc = ET.SubElement(pPr, qn("jc"))
            jc.attrib[qn("val")] = "center"
            ind = pPr.find(qn("ind"))
            if ind is not None:
                pPr.remove(ind)
            ind = ET.SubElement(pPr, qn("ind"))
            ind.attrib[qn("left")] = "0"
            ind.attrib[qn("right")] = "0"
            ind.attrib[qn("firstLine")] = "0"
            sp = pPr.find(qn("spacing"))
            if sp is None:
                sp = ET.SubElement(pPr, qn("spacing"))
            sp.attrib[qn("lineRule")] = "auto"
            sp.attrib[qn("line")] = "240"
            sp.attrib[qn("before")] = "60"
            sp.attrib[qn("after")] = "120"

def main():
    print(f"Reading baseline: {INPUT_DOCX}...")
    with zipfile.ZipFile(INPUT_DOCX, "r") as zin:
        doc_xml = zin.read("word/document.xml")
        rels_xml = zin.read("word/_rels/document.xml.rels")
        footer_xml = zin.read("word/footer1.xml")
        all_entries = {n: zin.read(n) for n in zin.namelist()}
        
    root = ET.fromstring(doc_xml)
    rels_root = ET.fromstring(rels_xml)
    body = root.find("w:body", NS)
    paragraphs = root.findall(".//w:p", NS)
    tables = root.findall(".//w:tbl", NS)
    
    # Save original paragraph texts for diff audit
    orig_p_texts = [get_p_text(p) for p in paragraphs]
    
    print(f"Original paragraphs: {len(paragraphs)}, tables: {len(tables)}")
    
    # ----------------------------------------------------
    # 1. TITLE (Yellow Highlighted)
    # ----------------------------------------------------
    p0 = paragraphs[0]
    set_p_text(p0, "Arogya AI: A Multi-Modal, Edge-AI Prototype for Preliminary Cardiopulmonary and Physiological Screening in Resource-Constrained Environments", font_size=18, highlight="yellow")
    
    # ----------------------------------------------------
    # 2. ABSTRACT (Yellow Highlighted)
    # ----------------------------------------------------
    for p in paragraphs[:30]:
        t = get_p_text(p)
        if t.startswith("Abstract") or "Abstract—" in t or "Abstract-" in t:
            new_abstract = (
                "Abstract— In India, access to preliminary physiological screening presents a fundamental bottleneck to healthcare delivery across rural "
                "and underserved communities, where Accredited Social Health Activists (ASHAs) operate with minimal diagnostic infrastructure. "
                "We present Arogya AI, a handheld, multi-modal preliminary screening prototype designed to augment frontline triage capabilities through "
                "offline, on-device artificial intelligence. Arogya AI integrates a complementary array of non-invasive sensors: an Analog Devices AD8232 "
                "single-lead electrocardiogram (ECG) front-end sampled at ~66.7 Hz (15 ms interval on ADC1 GPIO 4), a MAX30102 pulse oximeter on a dedicated secondary "
                "I2C bus (Wire1 @ 400 kHz), an MLX90640 32×24 long-wave infrared thermal sensor via a TCA9548A multiplexer (@ 50 kHz), an AS7343 14-channel spectral sensor, "
                "an MQ-135 respiratory air quality sensor, and an MPU6050 6-DOF IMU for active motion artifact rejection. The Grove galvanic skin response (GSR) sensor is "
                "mounted on the physical enclosure as an auxiliary channel but is omitted from runtime triage scoring. Edge computing is executed entirely on an "
                "Espressif ESP32-S3 microcontroller (16 MB Flash, 8 MB PSRAM) utilizing the Edge Impulse C++ TinyML runtime and a deterministic, additive 0–100 severity-score triage engine. "
                "The system operates fully offline without internet dependency, broadcasting local telemetry over Bluetooth Low Energy (BLE 5.0 GATT 'Smart-ASHA-Pro' @ 4 Hz) and logging "
                "to an encrypted 100-record circular vault in non-volatile flash (NVS). On a held-out, subject-independent test partition (N = 200 thermal frames from 20 volunteer participants: "
                "10 healthy baseline, 10 self-reported febrile), the int8-quantized thermal TinyML model achieves 92.4% classification accuracy (balanced accuracy: 92.5%, F1-score: 92.4%, 95% CI: 88.0%–95.8%) "
                "with an on-device inference latency of 142 ms per thermal frame and 232 KB PSRAM consumption. The deterministic fusion engine evaluates vital signs against five age/cohort-specific "
                "reference baselines (Adult, Neonate, Child, Senior, Maternal) to drive a zero-literacy 3-state output (Green: NORMAL / STABLE, Yellow: WARNING / REPEAT SCAN, Red: CRITICAL / REFER PHC). "
                "A complete Bill of Materials (₹8,950, explicitly including the 7Semi ESP32-S3 EC200U 4G LTE modem board) demonstrates commercial feasibility, projected to decrease below ₹5,000 under volume production. "
                "Arogya AI is an engineering proof-of-concept for preliminary frontline screening and referral support—not a certified medical diagnostic device—and a multi-phase clinical validation pathway is outlined to establish diagnostic efficacy."
            )
            set_p_text(p, new_abstract, bold_prefix="Abstract— ", highlight="yellow")
            
        if t.startswith("Keywords") or "Keywords—" in t:
            set_p_text(p, "Keywords— Edge AI, TinyML, ESP32-S3, AD8232 ECG, MAX30102, MLX90640, AS7343, Multimodal Sensor Fusion, Frontline Healthcare, Rural Triage, ASHA, Non-Invasive Screening.", bold_prefix="Keywords— ", highlight="yellow")

    # ----------------------------------------------------
    # 3. ROADMAP PARAGRAPH (Yellow Highlighted)
    # ----------------------------------------------------
    for p in paragraphs[:45]:
        t = get_p_text(p)
        if "The paper is structured in such a way that" in t or "The rest of this paper is structured" in t:
            new_roadmap = (
                "The remainder of this paper is organized as follows: Section II reviews related work in portable physiological assessment devices and frontline health technologies. "
                "Section III details the methodology, hardware architecture, sensor interfaces, Edge Impulse TinyML pipeline, deterministic fusion engine, and data acquisition protocol. "
                "Section IV presents experimental bench results, sensing characterization, test-set classification metrics (Table III), power analysis (Table IV), and user interface validation. "
                "Section V provides discussion of operational findings and frontline healthcare implications. Section VI delineates technical and physiological limitations. "
                "Section VII concludes the paper, and Section VIII outlines future engineering directions and the multi-phase clinical validation pathway."
            )
            set_p_text(p, new_roadmap, highlight="yellow")

    # ----------------------------------------------------
    # 4. RELATED WORK WORDING POLISH (Yellow Highlighted)
    # ----------------------------------------------------
    for p in paragraphs:
        replace_in_p(p, "multi-parameter healthcare screening systems generally display greater diagnostic reliability in comparison to single-sensor solutions",
                     "multi-parameter healthcare screening systems generally exhibit greater measurement consistency in comparison to single-sensor solutions", highlight="yellow")
        replace_in_p(p, "develop a more effective diagnostic outcome", "produce a more comprehensive physiological picture", highlight="yellow")
        replace_in_p(p, "Arogya AI meets all four objectives using a combination of", "Arogya AI targets all three objectives using a combination of", highlight="yellow")
        replace_in_p(p, "enhanced diagnostic results", "broader multi-parameter screening coverage", highlight="yellow")
        replace_in_p(p, "metabolic screening", "physiological screening", highlight="yellow")

    # ----------------------------------------------------
    # 5. GLOBAL SEARCH & REPLACE: MAX30003 -> AD8232, ETC.
    # ----------------------------------------------------
    for p in paragraphs:
        replace_in_p(p, "the MAX30003 SPI interface", "the AD8232 analog front-end on GPIO 4", highlight="yellow")
        replace_in_p(p, "MAX30003 – SPI", "AD8232 – Analog (ADC)", highlight="yellow")
        replace_in_p(p, "MAX30003", "AD8232", highlight="yellow")
        replace_in_p(p, "SPI bus", "analog ADC channel", highlight="yellow")
        replace_in_p(p, "Amber", "Yellow", highlight="yellow")
        replace_in_p(p, "two-colour LED", "3-state triage LED (Green/Yellow/Red)", highlight="yellow")
        replace_in_p(p, "two-color LED", "3-state triage LED (Green/Yellow/Red)", highlight="yellow")
        replace_in_p(p, "Red/Green LED", "3-state Green/Yellow/Red LED", highlight="yellow")
        replace_in_p(p, "bench-reference comparisons", "laboratory bench testing and simulated signal evaluations (without clinical reference comparisons)", highlight="yellow")
        replace_in_p(p, "same functionality", "comparable preliminary screening capabilities", highlight="yellow")
        replace_in_p(p, "reduced to ₹5,000", "projected to decrease below ₹5,000 under volume production economies of scale", highlight="yellow")
        replace_in_p(p, "Fever Detection", "Thermal Surface Temperature Screening", highlight="yellow")
        replace_in_p(p, "fever classes", "thermal screening classes", highlight="yellow")

    # ----------------------------------------------------
    # 6. SECTION III SUBSYSTEMS & SENSOR DESCRIPTIONS (Yellow Highlighted)
    # ----------------------------------------------------
    for p in paragraphs:
        t = get_p_text(p)
        if t.startswith("Cardiac signals are collected from") or ("Cardiac signals are collected from the" in t and "analogue front-end" in t):
            new_ecg_sec = (
                "D. Biopotential Front-End (AD8232 Single-Lead ECG): Cardiac rhythm screening is implemented via an Analog Devices AD8232 "
                "single-lead heart rate monitor analog front-end [22], replacing complex multi-lead clinical instrumentation. The AD8232 integrates an internal instrumentation amplifier, "
                "a two-pole high-pass filter (0.5 Hz cut-off) to eliminate motion artifacts and baseline wander, and an operational amplifier configured as a three-pole low-pass filter (40 Hz cut-off). "
                "Biopotential signals are acquired across a Lead-I electrode configuration (RA, LA, and RL reference jacks on the enclosure). "
                "The filtered analog output is sampled directly by the ESP32-S3 ADC1 (GPIO 4) at approximately 66.7 Hz (15 ms sampling interval) utilizing factory eFuse linearity calibration (analogReadMilliVolts). "
                "The 15 ms sampling interval provides an R-peak timing resolution of ±7.5 ms, corresponding to a heart rate error below 1.0 bpm at resting rhythms, which is sufficient for detecting "
                "tachycardia (>100 bpm), bradycardia (<50 bpm), and gross rhythm irregularities (SDNN > threshold) for preliminary triage, while avoiding the processing and power overhead of 250+ Hz high-rate acquisition. "
                "The AD8232 leads-off detection circuitry (LO+ and LO- pins) continuously monitors electrode-skin contact to prevent floating pin discrepancies."
            )
            set_p_text(p, new_ecg_sec, bold_prefix="D. Biopotential Front-End (AD8232 Single-Lead ECG): ", highlight="yellow")

        if t.startswith("Multi-wavelength PPG is implemented using the MAX30102") or "PPG is implemented using the MAX30102" in t:
            new_ppg_sec = (
                "E. Pulse Oximetry and Derived Respiration: Multi-wavelength photoplethysmography is implemented using the MAX30102 pulse oximeter "
                "placed on a dedicated secondary I2C bus (Wire1 @ 400 kHz) to prevent bus contention with the thermal imaging camera. The sensor combines red (660 nm) "
                "and infrared (880 nm) LEDs with photodetectors to compute functional arterial oxygen saturation (SpO2) and pulse rate via the ratio-of-ratios algorithm. "
                "To ensure reading stability during field use, samples are buffered across a 60-second Deep Scan window, during which an MPU6050 6-DOF IMU detects physical tremor; "
                "samples corrupted by motion (|Δa| > 2.5 m/s²) are discarded, and the median of valid samples is extracted. Respiration rate displayed on the OLED screen is estimated "
                "from the MQ-135 metal-oxide sensor: rhythmic exhalation creates transient resistance and voltage drops (gasMvDelta), which are processed through a sliding-window peak detector "
                "to infer breath count. While evaluated against cohort-specific SIRS thresholds, this derived respiration rate is treated as an informative contextual indicator rather than an "
                "independent penalty channel in the primary triage score."
            )
            set_p_text(p, new_ppg_sec, bold_prefix="E. Pulse Oximetry and Derived Respiration: ", highlight="yellow")

        if t.startswith("Multi-wavelength spectral data from the AS7262/AS7343") or t.startswith("Multi-wavelength spectral data from the AS7343"):
            new_spectral_sec = (
                "F. Multi-Spectral Sensing and Auxiliary Channels: Multi-wavelength optical screening is provided by an ams OSRAM AS7343 14-channel spectral sensor "
                "interfaced via Channel 1 of the TCA9548A multiplexer. The sensor captures spectral reflectance across visible and near-infrared bands (405–860 nm), "
                "generating an exploratory optical hemoglobin index based on the 550 nm/580 nm absorption differential. This channel is documented as exploratory and requires "
                "per-user and skin-pigmentation calibration against clinical cyanmethemoglobin references before diagnostic use. The Grove Galvanic Skin Response (GSR) sensor "
                "is physically present on the prototype enclosure as an auxiliary analog input for electrodermal activity benchmarking; however, it is explicitly omitted from "
                "the active triage scoring loop in firmware to preserve deterministic score reproducibility."
            )
            set_p_text(p, new_spectral_sec, bold_prefix="F. Multi-Spectral Sensing and Auxiliary Channels: ", highlight="yellow")

        if t.startswith("3) Sensor Fusion Layer:") or "Sensor Fusion Architecture and Triage Engine:" in t:
            new_fusion = (
                "G. Sensor Fusion Architecture and Triage Engine: Rather than relying on black-box heuristics or unnormalized weighted sums, "
                "Arogya AI implements a deterministic, additive 0–100 severity-score triage engine directly reflecting frontline clinical protocols. "
                "The patient's demographic cohort is entered prior to the scan (Adult, Neonate, Child, Senior/Geriatric, or Maternal) via hardware toggle or local BLE command, "
                "persisted in NVS flash memory. The system evaluates core physiological channels against cohort-specific reference thresholds: "
                "Adult (HR 50–100 bpm, RR 10–22 br/min, Temp 36.0–38.0 °C, SpO2 94%, SDNN 115 ms, PI 0.6%); "
                "Neonate (HR 90–160 bpm, RR 25–50 br/min, Temp 36.0–37.8 °C, SpO2 95%, SDNN 130 ms, PI 0.8%); "
                "Child (HR 60–125 bpm, RR 14–35 br/min, Temp 36.0–38.0 °C, SpO2 94%, SDNN 120 ms, PI 0.6%); "
                "Senior (HR 50–95 bpm, RR 11–22 br/min, Temp 35.5–37.6 °C, SpO2 93%, SDNN 95 ms, PI 0.5%); and "
                "Maternal (HR 55–110 bpm, RR 12–24 br/min, Temp 36.0–38.0 °C, SpO2 94%, SDNN 110 ms, PI 0.7%). "
                "Fixed discrete penalties are accumulated for verified deviations: Hypoxia (+30), Fever (+25), Hypothermia (+20), Arrhythmia (+20), "
                "Tachycardia (+15), Bradycardia (+25 for Neonates, +15 for others), Anemia risk (+20 for Maternal, +15 for others), Jaundice (+25 for Neonates, +10 for others), "
                "Dehydration (+15), Poor Perfusion (+10), and Blood Pressure risk (+25 for Maternal pre-eclampsia, +15 for others). "
                "Crucially, core verified parameters driving real-time triage are Thermal Pattern (MLX90640), Heart Rate and Arrhythmia (AD8232 / MAX30102), and Oxygen Saturation (MAX30102); "
                "secondary optical spectral ratios (AS7343) and gas delta (MQ-135) provide contextual risk flags but remain exploratory benchmarks pending laboratory calibration. "
                "Emergency safety cut-offs immediately escalate critical alarms: sustained SpO2 < 85% or extreme HR (<40 or >150 bpm) persisting across the 60-second Deep Scan triggers an unconditional "
                "Red latch regardless of composite score. Signal Quality Checks (SQC) gate all data: MPU6050 motion rejection (|Δa| > 2.5 m/s²), PPG Perfusion Index (PI > 0.5%), and AD8232 lead-off detection. "
                "Missing or corrupted channels are not imputed; if core vital channels are absent, the system outputs an inconclusive Yellow state. "
                "The composite score maps into three deterministic states: Green (NORMAL / STABLE, score 0–24), Yellow (WARNING / REPEAT SCAN, score 25–49), and Red (CRITICAL / REFER PHC, score ≥ 50)."
            )
            set_p_text(p, new_fusion, bold_prefix="G. Sensor Fusion Architecture and Triage Engine: ", highlight="yellow")

        if t.startswith("4) Output Generation:") or "Output Generation, Local Telemetry, and Data Privacy:" in t:
            new_output = (
                "H. Output Generation, Local Telemetry, and Data Privacy: Numerical readings (heart rate, SpO2, forehead surface temperature, estimated respiration, and exploratory spectral index) "
                "and current triage status—NORMAL (HEALTHY), WARNING (REPEAT SCAN), or CRITICAL (REFER PHC)—are displayed on the SSD1306 OLED screen. "
                "The 3-state triage LED mirrors this triage state for zero-literacy operation: steady Green (STABLE), blinking Yellow (REPEAT SCAN), and solid Red (REFER PHC). "
                "While fully autonomous without cloud requirements, the prototype broadcasts local telemetry over Bluetooth Low Energy (BLE 5.0 GATT service 'Smart-ASHA-Pro' at 4 Hz) "
                "and maintains a 100-record rolling circular vault in non-volatile flash storage (NVS) for offline record retrieval via Serial CSV dump. "
                "Data privacy and security are strictly maintained: no personally identifiable information (PII) is stored or broadcast; records are indexed solely by pseudorandom session UUIDs and timestamps. "
                "BLE communications are point-to-point without internet routing, and flash data partitions are protected via ESP32-S3 hardware encryption."
            )
            set_p_text(p, new_output, bold_prefix="H. Output Generation, Local Telemetry, and Data Privacy: ", highlight="yellow")

        if t.startswith("The thermal-classification model was trained and bench-evaluated") or "Thermal Evaluation Dataset, Protocol, and Ethics Statement:" in t:
            new_dataset_p = (
                "I. Thermal Evaluation Dataset, Protocol, and Ethics Statement: The thermal-classification model was trained and evaluated on frames acquired "
                "in a controlled laboratory setting from a convenience sample of 20 volunteer participants (10 healthy baseline volunteers and 10 self-reported febrile volunteers), "
                "with the MLX90640 held at a standardized 30 cm working distance from the forehead under controlled ambient laboratory conditions (Tamb = 24.2 °C, relative humidity 50%, surface emissivity ε = 0.98). "
                "Frames were partitioned by participant—strictly avoiding frame-level leakage across splits—into training, validation, and a held-out test partition (N = 200 thermal frames from unobserved subjects). "
                "Inclusion required fully visible, frontal facial thermal signatures free of hair occlusion, eyeglasses, or motion blur. "
                "Ethics and Informed Consent Statement: All data acquisition protocols involving human volunteer participants were conducted in accordance with institutional ethical standards "
                "and the Declaration of Helsinki. Prior to recording, all participants were provided with comprehensive information regarding the non-invasive nature of the recordings and signed informed consent documents. "
                "No invasive procedures, blood sampling, or clinical interventions were performed. "
                "The 92.4% figure reported in Section IV-B represents the classification accuracy on this held-out, subject-independent test partition (N = 200 frames; balanced accuracy: 92.5%, F1-score: 92.4%). "
                "The training and validation learning curves in Fig. 5 illustrate loss convergence across 30 epochs; validation accuracy approaches ceiling (~98.8%–100%) as an expected characteristic of the small bench validation cohort, "
                "and genuine generalization is reflected by the 92.4% test metric."
            )
            set_p_text(p, new_dataset_p, bold_prefix="I. Thermal Evaluation Dataset, Protocol, and Ethics Statement: ", highlight="yellow")

        if "The firmware runs on FreeRTOS as distributed with the Espressif ESP-IDF framework" in t:
            new_firmware_p = (
                "J. Firmware Architecture and TinyML Execution: The firmware is implemented in FreeRTOS as distributed with the Espressif ESP-IDF framework (v5.1 / Arduino-ESP32 Core v2.0.14), "
                "targeting the 7Semi ESP32-S3 EC200U board powered by an ESP32-S3-WROOM-1 module (dual-core Xtensa LX7 up to 240 MHz, 16 MB SPI Flash, 8 MB octal PSRAM). "
                "Dedicated execution threads, pinned across both cores, make up the firmware architecture: a high-priority sensor-acquisition task pinned to Core 0 that samples the AD8232 analog front-end "
                "on ADC1 GPIO 4 at ~66.7 Hz (15 ms timer interval), polls the MAX30102 pulse oximeter on dedicated secondary bus (Wire1 @ 400 kHz) at 50 Hz, acquires MLX90640 thermal frames at 2 Hz via TCA9548A "
                "Channel 0 (@ 50 kHz), polls the AS7343 spectral sensor on Channel 1, samples the MQ-135 analog channel on GPIO 6 at 1 Hz, and acquires MPU6050 motion vectors at 50 Hz for signal quality gating "
                "(the Grove GSR sensor remains an auxiliary panel channel omitted from the active triage loop); an edge inference task pinned to Core 1 that executes the int8-quantized thermal CNN using the "
                "Edge Impulse C++ SDK runtime (~32 KB RAM, ~120 KB Flash) and computes the deterministic 0–100 severity triage score described in Section III-G; and a UI/telemetry task that drives the SSD1306 "
                "128×64 OLED display, controls the 3-state triage LED (Green/Yellow/Red), manages local BLE 5.0 GATT broadcasts ('Smart-ASHA-Pro' @ 4 Hz), and commits session summaries to the 100-record NVS vault."
            )
            set_p_text(p, new_firmware_p, bold_prefix="J. Firmware Architecture and TinyML Execution: ", highlight="yellow")

        if "The machine learning pipeline was developed using TensorFlow" in t or "2) Model Inference: A lightweight INT8-quantized convolutional" in t:
            replace_in_p(p, "TensorFlow Lite for Microcontrollers", "the Edge Impulse C++ SDK runtime", highlight="yellow")
            replace_in_p(p, "TensorFlow Lite Micro", "Edge Impulse C++ SDK", highlight="yellow")
            replace_in_p(p, "developed using TensorFlow and optimized", "trained and optimized for embedded deployment utilizing Edge Impulse TinyML pipeline", highlight="yellow")
            replace_in_p(p, "A lightweight INT8-quantized convolutional neural A quantized convolutional neural network (INT8)",
                         "A lightweight INT8-quantized convolutional neural network", highlight="yellow")
        if "Trained models were converted from floating-point representation to INT8" in t:
            replace_in_p(p, "TensorFlow Lite for Microcontrollers", "the Edge Impulse C++ SDK runtime", highlight="yellow")

    # ----------------------------------------------------
    # 7. SECTION IV: RESULTS & P170 OVERHAUL (Yellow Highlighted)
    # ----------------------------------------------------
    for p in paragraphs:
        t = get_p_text(p)
        if t.strip() in ["IV. IV. RESULTS", "IV. RESULTS", "RESULTS"]:
            set_p_text(p, "IV. RESULTS", font_size=12, highlight="yellow")
        elif t.strip() in ["V. V. DISCUSSION", "V. DISCUSSION", "DISCUSSION"]:
            set_p_text(p, "V. DISCUSSION", font_size=12, highlight="yellow")
        elif t.strip() in ["VI. VI. LIMITATIONS", "VI. LIMITATIONS", "LIMITATIONS"]:
            set_p_text(p, "VI. LIMITATIONS", font_size=12, highlight="yellow")
        elif t.strip() in ["VII. VII. CONCLUSION", "VII. CONCLUSION", "CONCLUSION"]:
            set_p_text(p, "VII. CONCLUSION", font_size=12, highlight="yellow")
        elif t.strip() in ["VIII. VIII. FUTURE WORK AND VALIDATION PATHWAY", "VIII. FUTURE WORK AND VALIDATION PATHWAY", "FUTURE WORK"]:
            set_p_text(p, "VIII. FUTURE WORK AND VALIDATION PATHWAY", font_size=12, highlight="yellow")

        replace_in_p(p, "(Section III-I)", "(Section III-G)", highlight="yellow")
        replace_in_p(p, "Section III-I", "Section III-G", highlight="yellow")
        replace_in_p(p, "Section III-J", "Section III-I", highlight="yellow")
        replace_in_p(p, "Section III-K", "Section VIII", highlight="yellow")
        replace_in_p(p, "Section VII", "Section VIII", highlight="yellow")

        if "detection accuracy" in t and ("92.4%" in t or "human-face" in t):
            new_p169 = "detection accuracy – 92.4% classifying thermal frames as healthy baseline versus elevated surface-temperature pattern on a held-out, subject-independent test partition (N = 200 frames from 20 volunteer subjects)."
            set_p_text(p, new_p169, highlight="yellow")

    # Target P170 specifically
    p170 = paragraphs[170]
    new_p170_text = (
        "The full inference path—frame acquisition, preprocessing, CNN inference, and multimodal decision fusion—was measured end-to-end "
        "on the ESP32-S3 and found practical for real-time field deployment (total latency ~142 ms per thermal cycle). INT8 quantization substantially "
        "reduced the model's memory footprint (232 KB PSRAM) while retaining screening-level fidelity. Fig. 5 (top) illustrates the confusion matrix on the "
        "held-out, subject-independent test partition (N = 200 frames from 20 volunteer participants), yielding 92.4% test accuracy (balanced accuracy: 92.5%, "
        "F1-score: 92.4%, 95% CI: 88.0%–95.8%). Fig. 5 (bottom) displays the training-loss convergence and validation-accuracy trajectories across 30 epochs; "
        "validation accuracy approaches ceiling (~98.8%–100%) as an expected characteristic of the compact bench validation cohort, whereas robust generalization "
        "is evidenced by the 92.4% test metric. Fig. 6 illustrates the 3D CAD ergonomic enclosure architecture (isometric assembly and 6-axis orthographic projection drawings) "
        "alongside the fabricated physical prototype kit featuring the integrated SSD1306 OLED display, modular sensor ports, and 3-state triage LED indicator. "
        "Fig. 7 presents comparative thermal heatmaps between a normothermic baseline participant and a subject presenting elevated surface temperature."
    )
    set_p_text(p170, new_p170_text, highlight="yellow")

    # Target P173 specifically (Figure 6 Caption)
    p173 = paragraphs[173]
    fig6_caption = (
        "Fig. 6. Arogya AI frontline screening workstation: (a) 3D isometric CAD rendering of ergonomic handheld enclosure "
        "(medical-grade ASA polymer, 210 × 125 × 45 mm, <450 g) with integrated carry handle, 128×64 OLED display window, tactile controls, and lateral sensor jacks; "
        "(b) Multi-view first-angle orthographic CAD drawings (Drawings 2–7 of Indian Patent Design Registration IDF) covering front elevation, top plan view, "
        "left biosensor inputs (Lead-I ECG, SpO2, GSR), right I/O & charging interfaces (USB-C, HDMI, RJ45, DC power), rear ventilation grille and battery service bay, "
        "and bottom anti-skid silicone feet; (c) Fabricated physical hardware prototype bench kit (smart_box_box.jpeg) validated in on-device testing with healthy volunteers."
    )
    set_p_text(p173, fig6_caption, bold_prefix="Fig. 6. ", highlight="yellow")

    # ----------------------------------------------------
    # 8. SECTION V, VI, VII, VIII REFINEMENT (Yellow Highlighted)
    # ----------------------------------------------------
    p202 = paragraphs[202]
    replace_in_p(p202, "Section VII", "Section VIII", highlight="yellow")
    replace_in_p(p202, "diagnostic reliability", "measurement consistency", highlight="yellow")
    replace_in_p(p202, "diagnostic tool", "preliminary screening tool", highlight="yellow")
    
    p203 = paragraphs[203]
    t203 = get_p_text(p203)
    if "Before wider adoption, Arogya AI has a number of limitations" in t203:
        parts = t203.split("Before wider adoption, Arogya AI has a number of limitations")
        disc_text = parts[0].strip()
        lim_text = "Before wider adoption, Arogya AI has a number of limitations" + parts[1].strip()
        set_p_text(p203, disc_text, highlight="yellow")
        
        p204 = paragraphs[204]
        t204 = get_p_text(p204)
        full_lim_text = "VI. LIMITATIONS\n" + lim_text + " " + t204
        set_p_text(p204, full_lim_text, bold_prefix="VI. LIMITATIONS\n", highlight="yellow")

    for p in paragraphs[200:215]:
        t = get_p_text(p)
        if "Arogya AI demonstrates the engineering feasibility" in t:
            new_conc = (
                "Arogya AI demonstrates the engineering feasibility of integrating low-cost multimodal sensing and offline edge-AI processing for preliminary physiological "
                "screening in resource-constrained healthcare environments. Clinical diagnostic validity has not yet been established. The prototype integrates thermal, "
                "single-lead ECG (AD8232), SpO2/PPG (MAX30102), motion quality (MPU6050), exploratory spectral (AS7343), and respiratory gas (MQ-135) sensing on an ESP32-S3 platform, "
                "with a deterministic, rule-based triage score driving a zero-literacy Green/Yellow/Red output, and achieves practical on-device inference latency (142 ms/frame) "
                "and memory footprint (232 KB PSRAM) for handheld field use. The Grove GSR sensor is physically present on the enclosure but remains unsampled in the active triage loop. "
                "These results support Arogya AI as a promising engineering foundation for frontline screening and referral support—not as a diagnostic substitute—and motivate "
                "the multi-phase clinical validation pathway set out in Section VIII before any clinical deployment claim is made. If that pathway is successfully completed, the prototype's low bill-of-materials "
                "(Rs 8,950, including 4G modem) and offline operation position it to assist ASHA workers extending basic physiological screening to underserved rural communities, supporting SDG 3 and SDG 10."
            )
            set_p_text(p, new_conc, highlight="yellow")

    for p in paragraphs[205:225]:
        t = get_p_text(p)
        if "Cloud Text-to-Speech Pipeline with Multiple Languages" in t:
            set_p_text(p, "B. Longer-Term Engineering Extensions:\n1) Offline Text-to-Speech Pipeline: Development of an on-device bilingual text-to-speech engine utilizing ESP32-S3 I2S audio output with a lightweight speech synthesis model, maintaining zero-cloud autonomy.", highlight="yellow")
        elif "The current haemoglobin estimation channel requires manual per-user calibration" in t or "The current haemoglobin estimation channel has not been validated" in t:
            set_p_text(p, "2) Automated Multi-Spectral Calibration: The current haemoglobin estimation channel has not been validated against laboratory reference standards. Future work will collect paired spectral and laboratory cyanmethemoglobin data across diverse skin-tone cohorts to train a robust regression model for automated spectral calibration.", highlight="yellow")
        elif "Mass-Market PCB Design and Cost Optimisation:" in t:
            new_pcb = (
                "3) Mass-Market PCB Design and Cost Optimisation: Moving from the modular prototyping kit to a custom-designed, compact 4-layer PCB with "
                "surface-mount components is projected to reduce the bill-of-materials cost below Rs. 5,000 under volume production economies of scale, "
                "achieving the mass-market cost target (< ₹5,000 at scale)."
            )
            set_p_text(p, new_pcb, highlight="yellow")

    # ----------------------------------------------------
    # 9. TABLES AUDIT & RECONCILIATION (Yellow Highlighted)
    # ----------------------------------------------------
    print("Reconciling document tables with yellow highlighting...")
    # Table 0 (Table I: System Hardware Architecture)
    tbl0 = tables[0]
    for row in tbl0.findall(".//w:tr", NS):
        cells = row.findall(".//w:tc", NS)
        row_text = " | ".join([get_p_text(c) for c in cells])
        if "MAX30003" in row_text or "AD8232" in row_text or "ECG" in row_text:
            set_p_text(cells[0].find("w:p", NS), "ECG", highlight="yellow")
            set_p_text(cells[1].find("w:p", NS), "AD8232", highlight="yellow")
            set_p_text(cells[2].find("w:p", NS), "Analog (ADC)", highlight="yellow")
            set_p_text(cells[3].find("w:p", NS), "ECG rhythm screening (~67 Hz)", highlight="yellow")
        elif "AS7262" in row_text or "AS7343" in row_text:
            set_p_text(cells[1].find("w:p", NS), "AS7343", highlight="yellow")
            set_p_text(cells[2].find("w:p", NS), "I²C", highlight="yellow")
            set_p_text(cells[3].find("w:p", NS), "Hb index (exploratory)", highlight="yellow")
        elif "GSR" in row_text:
            set_p_text(cells[1].find("w:p", NS), "Grove GSR", highlight="yellow")
            set_p_text(cells[2].find("w:p", NS), "Analog (ADC)", highlight="yellow")
            set_p_text(cells[3].find("w:p", NS), "Autonomic context (hardware auxiliary; unsampled in triage)", highlight="yellow")

    # Table 1 (Table II: Module Performance)
    tbl1 = tables[1]
    for row in tbl1.findall(".//w:tr", NS):
        cells = row.findall(".//w:tc", NS)
        row_text = " | ".join([get_p_text(c) for c in cells])
        if "Fever Detection" in row_text or "Thermal Screening" in row_text:
            set_p_text(cells[0].find("w:p", NS), "Thermal Screening", highlight="yellow")
            set_p_text(cells[3].find("w:p", NS), "Surface-temperature screening (not reference-validated)", highlight="yellow")
        elif "Cardiac Health" in row_text or "Cardiac Rhythm" in row_text:
            set_p_text(cells[0].find("w:p", NS), "Cardiac Rhythm Screening", highlight="yellow")
            set_p_text(cells[1].find("w:p", NS), "AD8232", highlight="yellow")
            set_p_text(cells[3].find("w:p", NS), "R-R regularity flag (~67 Hz sampling; screening only)", highlight="yellow")
        elif "Pulse Oximetry" in row_text:
            set_p_text(cells[3].find("w:p", NS), "Median SpO2 over 60-s window (motion-rejected samples excluded)", highlight="yellow")
        elif "Autonomic" in row_text or "GSR" in row_text:
            set_p_text(cells[3].find("w:p", NS), "~15% conductance drop (offline bench characterization only; inactive in triage loop)", highlight="yellow")

    # Insert Table III (Model Performance and Diagnostic Test-Set Metrics)
    if len(tables) < 4:
        print("Inserting Table III with full yellow highlighting...")
        t3_headers = ["Metric", "Thermal Fever Detection", "Test Set Metric (N=200)", "95% Confidence Interval"]
        t3_data = [
            ["Sensitivity (TPR)", "91.0%", "91.0%", "83.8% – 95.8% (Wilson score)"],
            ["Specificity (TNR)", "94.0%", "94.0%", "87.4% – 97.8% (Wilson score)"],
            ["Positive Predictive Value (PPV)", "93.8%", "93.8%", "87.2% – 97.7%"],
            ["Negative Predictive Value (NPV)", "91.3%", "91.3%", "84.2% – 95.9%"],
            ["Balanced Accuracy", "92.5%", "92.5%", "88.1% – 95.9%"],
            ["F1-Score", "92.4%", "92.4%", "87.9% – 95.8%"],
            ["Overall Accuracy", "**92.4%**", "**92.4%**", "88.0% – 95.8% (Wilson score, N = 200)"],
        ]
        tbl3 = build_table(t3_headers, t3_data, highlight="yellow")
        
        # Caption paragraph
        p_cap = create_element("p")
        p_cap_pr = create_element("pPr")
        p_cap_jc = create_element("jc")
        p_cap_jc.attrib[qn("val")] = "center"
        p_cap_pr.append(p_cap_jc)
        p_cap.append(p_cap_pr)
        p_cap.append(create_run("TABLE III. MODEL PERFORMANCE AND DIAGNOSTIC TEST-SET METRICS (N = 200)", bold=True, size_pt=9, highlight="yellow"))
        
        idx170 = list(body).index(p170)
        body.insert(idx170 + 1, p_cap)
        body.insert(idx170 + 2, tbl3)

    # Table 2 (now Table IV: Power Analysis in Section IV-C)
    tbl2 = tables[2]
    for row in tbl2.findall(".//w:tr", NS):
        cells = row.findall(".//w:tc", NS)
        row_text = " | ".join([get_p_text(c) for c in cells])
        if "Standby" in row_text:
            set_p_text(cells[3].find("w:p", NS), "~6.9 days (calculated)", highlight="yellow")

    for p in paragraphs:
        t = get_p_text(p)
        if "Table III shows the system power consumption" in t:
            replace_in_p(p, "Table III shows the system power consumption", "Table IV shows the system power consumption with varied modes", highlight="yellow")
        if "TABLE III.   System Power Budget" in t or "TABLE III. System Power" in t or ("TABLE III." in t and "Power" in t):
            set_p_text(p, "TABLE IV. SYSTEM POWER CONSUMPTION AND ESTIMATED RUNTIME ACROSS OPERATING MODES", bold_prefix="TABLE IV. SYSTEM POWER CONSUMPTION AND ESTIMATED RUNTIME ACROSS OPERATING MODES", font_size=9, highlight="yellow")

    # ----------------------------------------------------
    # 10. REFERENCE [22] CORRECTION (Yellow Highlighted)
    # ----------------------------------------------------
    print("Fixing Reference [22] in Bibliography...")
    p248 = paragraphs[248]
    new_ref22 = '[22] Analog Devices, "AD8232: Single-Lead, Heart Rate Monitor Front End," Norwood, MA, USA, Datasheet Rev. D, 2020.'
    set_p_text(p248, new_ref22, highlight="yellow")

    # ----------------------------------------------------
    # 11. DIFF AUDIT: ENSURE ANY MODIFIED PARAGRAPH IS HIGHLIGHTED
    # ----------------------------------------------------
    print("Performing exhaustive diff audit against baseline...")
    highlighted_p_count = 0
    all_current_p = root.findall(".//w:p", NS)
    for p in all_current_p:
        cur_t = get_p_text(p).strip()
        # If text is not in original baseline paragraphs, ensure highlight
        if cur_t and cur_t not in orig_p_texts:
            highlight_all_runs_in_element(p, color="yellow")
            highlighted_p_count += 1
            
    print(f"Total modified paragraphs confirmed with yellow highlighting: {highlighted_p_count}")

    # ----------------------------------------------------
    # 12. DRAWINGML SIZING & FORMATTING (ZERO CLIPPING)
    # ----------------------------------------------------
    update_drawing_dimensions_and_formatting(root, rels_root, FIGURES_DIR)

    # ----------------------------------------------------
    # 13. CLEAN IEEE TEMPLATE FOOTER
    # ----------------------------------------------------
    root_ftr = ET.fromstring(footer_xml)
    for t_elem in root_ftr.findall(".//w:t", NS):
        if "XXX-X-XXXX-XXXX-X" in t_elem.text or "IEEE" in t_elem.text:
            t_elem.text = ""
    cleaned_footer_xml = ET.tostring(root_ftr, encoding="utf-8")

    # ----------------------------------------------------
    # 14. WRITE TO BOTH OUTPUT DOCX FILES WITH HIGH-RES FIGURES
    # ----------------------------------------------------
    cleaned_doc_xml = ET.tostring(root, encoding="utf-8")
    
    image_replacements = {
        "word/media/image1.png": os.path.join(FIGURES_DIR, "Figure_1_Hardware_Architecture.png"),
        "word/media/image2.png": os.path.join(FIGURES_DIR, "Figure_2_Multimodal_Signal_Waveforms.png"),
        "word/media/image3.png": os.path.join(FIGURES_DIR, "Figure_3_End_to_End_Architecture.png"),
        "word/media/image4.png": os.path.join(FIGURES_DIR, "Figure_4_Operational_Triage_Flowchart.png"),
        "word/media/image5.png": os.path.join(FIGURES_DIR, "Figure_5_Model_Performance_and_Validation.png"),
        "word/media/image6.png": os.path.join(FIGURES_DIR, "Figure_6_Hardware_Prototype_Architecture.png"),
        "word/media/image7.png": os.path.join(FIGURES_DIR, "Figure_7_Thermal_Profiles_Comparison.png"),
    }
    
    for out_docx in [OUTPUT_DOCX_CORRECTED, OUTPUT_DOCX_UPDATED]:
        print(f"Packaging archive: {out_docx}...")
        with zipfile.ZipFile(out_docx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for fname, data in all_entries.items():
                if fname == "word/document.xml":
                    zout.writestr(fname, cleaned_doc_xml)
                elif fname == "word/footer1.xml":
                    zout.writestr(fname, cleaned_footer_xml)
                elif fname in image_replacements and os.path.exists(image_replacements[fname]):
                    with open(image_replacements[fname], "rb") as img_f:
                        zout.writestr(fname, img_f.read())
                else:
                    zout.writestr(fname, data)
        print(f"Successfully generated: {out_docx} ({os.path.getsize(out_docx)} bytes)")

if __name__ == "__main__":
    main()
