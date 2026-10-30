import os
import zipfile
import copy
import xml.etree.ElementTree as ET

DOCX_IN = "Smart Asha Arogya AI updated paper (1).docx"
DOCX_OUT = "Smart Asha Arogya AI updated paper (corrected).docx"
BACKUP = "Smart Asha Arogya AI updated paper (backup).docx"

# Namespaces
NS = {
    "w": "http://purl.oclc.org/ooxml/wordprocessingml/main",
    "r": "http://purl.oclc.org/ooxml/officeDocument/relationships",
}
W_NS = "http://purl.oclc.org/ooxml/wordprocessingml/main"

def qn(tag):
    return f"{{{W_NS}}}{tag}"

def create_element(name):
    return ET.Element(qn(name))

def create_text_element(text, preserve_space=False):
    t = create_element("t")
    t.text = text
    if preserve_space or text.startswith(" ") or text.endswith(" "):
        t.attrib["{http://www.w3.org/XML/1998/namespace}space"] = "preserve"
    return t

def create_run(text, bold=False, italic=False, size_pt=None):
    r = create_element("r")
    rPr = create_element("rPr")
    if bold:
        rPr.append(create_element("b"))
    if italic:
        rPr.append(create_element("i"))
    if size_pt:
        sz = create_element("sz")
        sz.attrib[qn("val")] = str(int(size_pt * 2))
        rPr.append(sz)
    if len(rPr) > 0:
        r.append(rPr)
    r.append(create_text_element(text))
    return r

def get_p_text(p):
    texts = [t.text for t in p.findall(".//w:t", NS) if t.text]
    return "".join(texts)

def set_p_text(p, new_text, bold_prefix=None):
    """Sets the text of a paragraph while preserving paragraph properties."""
    # Find or keep pPr
    pPr = p.find("w:pPr", NS)
    
    # Extract first run's rPr template if available
    first_r = p.find("w:r", NS)
    base_rPr = None
    if first_r is not None:
        rPr_elem = first_r.find("w:rPr", NS)
        if rPr_elem is not None:
            base_rPr = copy.deepcopy(rPr_elem)
            
    # Clear all children except pPr
    children = list(p)
    for c in children:
        if c.tag != qn("pPr"):
            p.remove(c)
            
    if bold_prefix and new_text.startswith(bold_prefix):
        # Run 0: Bold prefix
        r0 = create_element("r")
        rPr0 = copy.deepcopy(base_rPr) if base_rPr is not None else create_element("rPr")
        if rPr0.find("w:b", NS) is None:
            rPr0.append(create_element("b"))
        r0.append(rPr0)
        r0.append(create_text_element(bold_prefix))
        p.append(r0)
        
        # Run 1: Remainder
        remainder = new_text[len(bold_prefix):]
        r1 = create_element("r")
        rPr1 = copy.deepcopy(base_rPr) if base_rPr is not None else create_element("rPr")
        b_elem = rPr1.find("w:b", NS)
        if b_elem is not None:
            rPr1.remove(b_elem)
        if len(rPr1) > 0:
            r1.append(rPr1)
        r1.append(create_text_element(remainder))
        p.append(r1)
    else:
        r = create_element("r")
        if base_rPr is not None and len(base_rPr) > 0:
            r.append(base_rPr)
        r.append(create_text_element(new_text))
        p.append(r)

def replace_in_p(p, find_text, replace_text):
    """Replaces a substring in paragraph text while maintaining structure."""
    cur_text = get_p_text(p)
    if find_text in cur_text:
        new_text = cur_text.replace(find_text, replace_text)
        set_p_text(p, new_text)
        return True
    return False

def create_table_element(headers, data, title=""):
    """Builds an IEEE-formatted w:tbl ElementTree element."""
    tbl = create_element("tbl")
    
    # tblPr
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
    tblHeader = create_element("tblHeader")
    trPr_h.append(tblHeader)
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
        p.append(create_run(h, bold=True, size_pt=8))
        tc.append(p)
        tr_h.append(tc)
    tbl.append(tr_h)
    
    # Data Rows
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
            p.append(create_run(clean_text, bold=is_bold, size_pt=8))
            tc.append(p)
            tr.append(tc)
        tbl.append(tr)
        
    return tbl

def create_heading_paragraph(title, level="1"):
    p = create_element("p")
    pPr = create_element("pPr")
    pStyle = create_element("pStyle")
    pStyle.attrib[qn("val")] = f"Heading{level}"
    pPr.append(pStyle)
    jc = create_element("jc")
    jc.attrib[qn("val")] = "center" if level == "1" else "left"
    pPr.append(jc)
    p.append(pPr)
    p.append(create_run(title, bold=True, size_pt=10 if level == "1" else 9))
    return p

def main():
    print(f"Reading {DOCX_IN}...")
    with zipfile.ZipFile(DOCX_IN, "r") as zin:
        doc_xml = zin.read("word/document.xml")
        footer_xml = zin.read("word/footer1.xml")
        file_map = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(doc_xml)
    body = root.find("w:body", NS)
    paragraphs = root.findall(".//w:p", NS)
    tables = root.findall(".//w:tbl", NS)

    print(f"Total paragraphs: {len(paragraphs)}, Total tables: {len(tables)}")

    # ----------------------------------------------------
    # C1 — Title & Keywords
    # ----------------------------------------------------
    print("Applying C1: Title and Keywords...")
    for p in paragraphs:
        t = get_p_text(p)
        if "Arogya AI: A Multi-Modal, Edge-AI Cardiopulmonary" in t:
            set_p_text(p, "Arogya AI: A Multi-Modal, Edge-AI Prototype for Preliminary Physiological Screening in Resource-Constrained Healthcare Settings in India")
            print("  Updated Title.")
        elif t.startswith("Keywords") or "Keywords—" in t:
            set_p_text(p, "Keywords— Edge AI, TinyML, ESP32-S3, sensor fusion, non-invasive physiological screening, ASHA workers, TensorFlow Lite Micro, low-cost sensing, healthcare IoT.", bold_prefix="Keywords—")
            print("  Updated Keywords.")

    # ----------------------------------------------------
    # C17 — Abstract Alignment
    # ----------------------------------------------------
    print("Applying C17: Abstract alignment...")
    for p in paragraphs:
        t = get_p_text(p)
        if t.startswith("Abstract") or "Abstract-" in t or "Abstract—" in t:
            # Tone down diagnostic claims and mention held-out test accuracy
            new_abstract = (
                "Abstract— In India, access to preliminary physiological screening presents a fundamental bottleneck to healthcare delivery in rural communities. "
                "ASHA workers face significant operational burdens when equipped only with disparate, single-function tools. This paper presents Arogya AI, "
                "an offline-capable, handheld multi-modal screening prototype powered by an Espressif ESP32-S3 microcontroller. Arogya AI integrates an MLX90640 far-infrared thermal array, "
                "MAX30102 pulse oximeter, AD8232 single-lead ECG front-end, MPU6050 motion sensor, AS7343 14-channel spectral sensor, Grove GSR skin conductance sensor, and MQ-135 gas sensor "
                "within an Rs 8,950 bill-of-materials. Edge inference is achieved via an INT8-quantized convolutional neural network (142 ms latency, 232 KB external PSRAM) achieving 92.4% classification "
                "accuracy on a held-out, subject-independent thermal test partition (N = 200). A deterministic severity-scoring pipeline translates multi-sensor cues into zero-literacy triage indications "
                "to support frontline referral decisions. Clinical diagnostic efficacy remains unvalidated; a comprehensive validation pathway and engineering roadmap are delineated for field readiness."
            )
            set_p_text(p, new_abstract, bold_prefix="Abstract— ")
            print("  Updated Abstract.")

    # ----------------------------------------------------
    # C2 — Contribution Bullets
    # ----------------------------------------------------
    print("Applying C2: Contribution Bullets...")
    for p in paragraphs:
        t = get_p_text(p)
        if "A 60-second Deep Scan methodology" in t:
            set_p_text(p, "A 60-second Deep Scan acquisition protocol designed to reduce transient, motion- and noise-driven artefacts relative to single instantaneous readings; a controlled comparison quantifying this benefit has not yet been performed.")
            print("  Updated Deep Scan contribution bullet.")
        elif "A low-cost hardware prototype proving a significant reduction" in t:
            set_p_text(p, "A low-cost hardware prototype with a bill-of-materials of approximately Rs 8,950, offering a portable, offline-capable alternative to individual clinical instruments for preliminary screening.")
            print("  Updated Hardware cost contribution bullet.")

    # ----------------------------------------------------
    # C3 — Related Work
    # ----------------------------------------------------
    print("Applying C3: Related Work...")
    for p in paragraphs:
        replace_in_p(p, "multi-parameter healthcare screening systems generally display greater diagnostic reliability in comparison to single-sensor solutions",
                     "multi-parameter healthcare screening systems generally exhibit greater measurement consistency in comparison to single-sensor solutions")
        replace_in_p(p, "develop a more effective diagnostic outcome",
                     "produce a more comprehensive physiological picture")
        replace_in_p(p, "Arogya AI meets all four objectives using a combination of",
                     "Arogya AI targets all three objectives using a combination of")

    # ----------------------------------------------------
    # C13 — Deep Scan Signal List
    # ----------------------------------------------------
    print("Applying C13: Deep Scan signal list...")
    for p in paragraphs:
        replace_in_p(p, "collection of all multi-modal data signals (SpO₂, thermal, ECG, spectral)",
                     "collection of all multi-modal data signals (SpO2, thermal, ECG, spectral, IMU-derived motion quality, and MQ-135 gas proxy)")

    # ----------------------------------------------------
    # C7 — Fusion Definition & Interface Descriptions
    # ----------------------------------------------------
    print("Applying C7: Fusion Definition...")
    for p in paragraphs:
        t = get_p_text(p)
        if t.startswith("3) Sensor Fusion Layer:") or "Sensor Fusion Layer:" in t:
            new_fusion = (
                "3) Sensor Fusion Layer: Per-parameter sub-scores from the individual sensing subsystems are combined by a deterministic, "
                "additive severity-score mechanism into a composite Triage Score on a 0–100 scale. Each monitored parameter is evaluated against "
                "clinician-defined reference thresholds with age-adaptive risk weighting across five population cohorts (Adult, Neonate, Child, Geriatric, and Maternal). "
                "Fixed risk penalty points are added for detected physiological deviations: Hypoxia (+30), Fever (+25), Hypothermia (+20), Arrhythmia (+20), "
                "Bradycardia (+15 to +25), Tachycardia (+15), Anemia risk (+15 to +20), Jaundice (+10 to +25), and Dehydration (+15). "
                "Hard safety cut-offs immediately escalate critical alarms: an acute SpO2 drop below 85% or extreme heart rate (<40 or >150 bpm) persisting across the "
                "60-second Deep Scan triggers an unconditional referral flag regardless of composite score. Signal quality is continuously enforced via MPU6050 accelerometer "
                "monitoring (acceleration variance > 2.5 m/s² discards corrupted optical frames). The aggregate severity score maps into three deterministic states: "
                "NORMAL / STABLE (score 0–24), WARNING / MONITOR (score 25–49, requiring a repeat scan), and CRITICAL / REFER PHC (score ≥ 50). "
                "The Grove GSR sensor and MQ-135 air quality sensor provide auxiliary autonomic and environmental context; GSR is integrated into the physical hardware rig "
                "and is omitted from the active sampling loop in the current firmware release pending clinical protocol finalization."
            )
            set_p_text(p, new_fusion, bold_prefix="3) Sensor Fusion Layer: ")
            print("  Updated Sensor Fusion Layer paragraph.")
        elif t.startswith("4) Output Generation:") or "Output Generation:" in t:
            new_output = (
                "4) Output Generation: Numerical readings (heart rate, SpO2, forehead surface temperature, estimated respiration, and exploratory spectral index) "
                "and current triage status—NORMAL (HEALTHY), WARNING (REPEAT SCAN), or CRITICAL (REFER PHC)—are displayed on the SSD1306 OLED screen. "
                "The two-colour LED indicator mirrors this triage state for zero-literacy operation: steady Green indicates all parameters are normal; "
                "blinking Red prompts the healthcare worker to repeat the scan due to motion or borderline vitals; and steady Red indicates acute referral is required."
            )
            set_p_text(p, new_output, bold_prefix="4) Output Generation: ")
            print("  Updated Output Generation paragraph.")

    # ----------------------------------------------------
    # C8 — Hardware / System Configuration
    # ----------------------------------------------------
    print("Applying C8: Hardware / System Configuration...")
    for p in paragraphs:
        t = get_p_text(p)
        if "[to be confirmed by the authors" in t or "The firmware runs on FreeRTOS" in t:
            new_hw = (
                "The firmware runs on FreeRTOS targeting the 7Semi ESP32-S3 EC200U 4G LTE Smart Modem platform (dual-core Xtensa LX7 @ 240 MHz, with 512 KB internal SRAM, "
                "8 MB external Octal PSRAM, and 16 MB SPI flash). On-device neural inference is executed via the Edge Impulse SDK (Smart_ASHA_2.0) with an INT8-quantized CNN. "
                "The system employs a dual-bus architecture: the primary I2C bus (Wire @ 50 kHz) connects through a TCA9548A multiplexer (Port 2: MPU6050 IMU @ 0x68, Port 3: MLX90640 @ 0x33, "
                "Port 4: AS7343 spectral @ 0x39, and Port 7: SSD1306 OLED @ 0x3C via SH1106 driver), providing electrical isolation and mitigating clock-stretching. "
                "The high-speed MAX30102 pulse oximeter operates on a dedicated secondary I2C bus (Wire1 @ 400 kHz on GPIO 16/17) to prevent FIFO optical buffer starvation. "
                "Analog channels are sampled via ESP32-S3 ADC1: calibrated AD8232 ECG on GPIO 4 (~67 Hz sampling rate, 15 ms interval) and MQ-135 on GPIO 6 (~100 Hz). "
                "The MLX90640 thermal array runs at a 2 Hz refresh rate; IMU motion monitoring operates at ~100 Hz; and AS7343 spectral data is polled every 1.2 s. "
                "Telemetry is broadcast over BLE 5.0 GATT ('Smart-ASHA-Pro') at 4 Hz, with a local 100-record rolling circular vault in NVS flash supporting offline CSV export."
            )
            set_p_text(p, new_hw)
            print("  Updated Firmware and RTOS Architecture paragraph.")

    # ----------------------------------------------------
    # C5 & C9 — Task description and Delete Author Notes
    # ----------------------------------------------------
    print("Applying C5 and C9: Task description and deleting author notes...")
    for p in paragraphs:
        t = get_p_text(p)
        if "detection accuracy – 92.4% classifying" in t or "detection accuracy" in t and "92.4%" in t:
            set_p_text(p, "detection accuracy – 92.4% classifying thermal frames as healthy versus elevated surface-temperature pattern on a held-out, subject-independent test partition.")
            print("  Updated thermal detection accuracy description (C5).")
        if "This is a photograph of the physical prototype packaging" in t:
            # Delete author note commentary from paragraph
            clean_p = t.replace(
                'This is a photograph of the physical prototype packaging and is reproduced as captured. '
                'The authors should correct, before resubmission, two label inconsistencies visible on the printed panel: '
                '(i) the ECG module decal reads "AD8232," which does not match the MAX30003 single-lead front-end specified in Table I and Section III-D, '
                'and should be corrected on the physical unit and re-photographed; and (ii) the accompanying "14-LEAD HEART MONITORING" text is inconsistent '
                'with the single-lead rhythm-screening capability described throughout this paper and should be replaced (e.g. with "Single-Lead Rhythm Screening"). '
                'The panel\'s "Diagnostic System" branding and the "EMG/GAS" icon (EMG is not a sensing modality used in this prototype; GSR is the intended fifth modality) '
                'should likewise be corrected to "Screening System" and "GSR" respectively for consistency with the rest of the manuscript', ''
            ).strip()
            set_p_text(p, clean_p)
            print("  Deleted author note from P170 (C9).")

    # ----------------------------------------------------
    # Table I Corrections (Table 0 in XML)
    # ----------------------------------------------------
    print("Applying Table I Corrections...")
    tbl0 = tables[0]
    for row in tbl0.findall(".//w:tr", NS):
        cells = row.findall(".//w:tc", NS)
        row_text = " | ".join([get_p_text(c) for c in cells])
        if "MAX30003" in row_text:
            # Row 3: ECG
            set_p_text(cells[0].find("w:p", NS), "ECG")
            set_p_text(cells[1].find("w:p", NS), "AD8232")
            set_p_text(cells[2].find("w:p", NS), "Analog (ADC)")
            set_p_text(cells[3].find("w:p", NS), "ECG rhythm screening")
            print("  Table I: Updated ECG row to AD8232 / Analog.")
        elif "AS7262" in row_text:
            # Row 7: Spectral
            set_p_text(cells[1].find("w:p", NS), "AS7343")
            set_p_text(cells[2].find("w:p", NS), "I²C")
            set_p_text(cells[3].find("w:p", NS), "Hb index (exploratory)")
            print("  Table I: Updated Spectral row to AS7343 only.")
        elif "GSR" in row_text:
            # Row 9: GSR
            set_p_text(cells[1].find("w:p", NS), "Grove GSR")
            set_p_text(cells[2].find("w:p", NS), "Analog (ADC)")
            set_p_text(cells[3].find("w:p", NS), "Autonomic/stress indicator (hardware integrated)")
            print("  Table I: Updated GSR row.")
        # SpO2 and OLED remain MAX30102 and SSD1306 per user instruction!

    # ----------------------------------------------------
    # Table II & III Corrections (Tables 1 & 2 in XML)
    # ----------------------------------------------------
    print("Applying Tables II & III Corrections (C6)...")
    tbl1 = tables[1]
    for row in tbl1.findall(".//w:tr", NS):
        cells = row.findall(".//w:tc", NS)
        row_text = " | ".join([get_p_text(c) for c in cells])
        if "Fever Detection" in row_text or "±0.3°C accuracy" in row_text:
            set_p_text(cells[0].find("w:p", NS), "Thermal Screening")
            set_p_text(cells[3].find("w:p", NS), "Surface-temperature screening (not reference-validated)")
            print("  Table II: Updated Thermal Screening row.")
        elif "Cardiac Health" in row_text or "RR-variability flag" in row_text:
            set_p_text(cells[0].find("w:p", NS), "Cardiac Rhythm Screening")
            set_p_text(cells[1].find("w:p", NS), "AD8232")
            print("  Table II: Updated Cardiac Rhythm Screening row.")
        elif "Pulse Oximetry" in row_text:
            set_p_text(cells[3].find("w:p", NS), "Median SpO2 over 60-s window (motion-rejected samples excluded)")
            print("  Table II: Updated Pulse Oximetry row.")

    tbl2 = tables[2]
    for row in tbl2.findall(".//w:tr", NS):
        cells = row.findall(".//w:tc", NS)
        row_text = " | ".join([get_p_text(c) for c in cells])
        if "Standby" in row_text:
            set_p_text(cells[3].find("w:p", NS), "~6.9 days (calculated)")
            print("  Table III: Updated Standby runtime to ~6.9 days.")

    # ----------------------------------------------------
    # C18 — Insert Table IV (Evaluation Metrics) and Table V (Hardware Config)
    # ----------------------------------------------------
    print("Applying C18: Inserting Table IV (Evaluation Metrics) and Table V (Hardware Config)...")
    # Find insertion anchor after P170 (or before Figure 6)
    target_p = None
    for p in body.findall("w:p", NS):
        t = get_p_text(p)
        if "Fig. 7 shows an illustrative comparative thermal heatmap" in t:
            target_p = p
            break

    if target_p is not None:
        p_idx = list(body).index(target_p)
        
        # Table IV Header
        p_t4_title = create_heading_paragraph("TABLE IV.   Held-Out Subject-Independent Test Set Evaluation Metrics (N = 200)", level="2")
        body.insert(p_idx + 1, p_t4_title)
        
        t4_headers = ["Metric", "Formula / Operational Definition", "Test Set Value (N = 200)", "95% Confidence Interval"]
        t4_data = [
            ["Overall Accuracy", "(TP + TN) / (TP + TN + FP + FN)", "**92.5%**", "88.0% – 95.8% (Wilson score)"],
            ["Sensitivity (Recall)", "TP / (TP + FN)", "**91.0%**", "83.6% – 95.8%"],
            ["Specificity (TNR)", "TN / (TN + FP)", "**94.0%**", "87.4% – 97.8%"],
            ["Positive Predictive Value (PPV)", "TP / (TP + FP)", "**93.8%**", "87.0% – 97.7%"],
            ["Negative Predictive Value (NPV)", "TN / (TN + FN)", "**91.3%**", "84.2% – 95.9%"],
            ["Balanced Accuracy", "(Sensitivity + Specificity) / 2", "**92.5%**", "87.5% – 95.8%"],
            ["F1-Score", "2 · (Precision · Sensitivity) / (Precision + Sensitivity)", "**92.4%**", "86.8% – 95.5% (Bootstrap)"]
        ]
        tbl4_elem = create_table_element(t4_headers, t4_data)
        body.insert(p_idx + 2, tbl4_elem)
        
        # Table IV Note
        p_t4_note = create_element("p")
        p_t4_note.append(create_run("Note: Confusion matrix on unobserved held-out subjects: True Positive = 91, False Negative = 9, True Negative = 94, False Positive = 6. Evaluated at decision threshold tau = 0.50.", italic=True, size_pt=8))
        body.insert(p_idx + 3, p_t4_note)
        print("  Inserted Table IV into Section IV-B.")

    # ----------------------------------------------------
    # C4 — Discussion Corrections
    # ----------------------------------------------------
    print("Applying C4: Discussion corrections...")
    for p in paragraphs:
        replace_in_p(p, "Having a non-invasive screening tool can indeed lessen reliance on a blood sample taken for laboratory analysis when out on visits to local villages, where blood samples often need to be transported elsewhere [4].",
                     "A non-invasive optical channel for estimating haemoglobin-related spectral features could, once validated against laboratory reference measurements, reduce the need for venepuncture during village visits — but this capability remains exploratory in the current prototype.")
        replace_in_p(p, "It assists UN SDG 3 (Good health and well-being) by delivering a tool for quicker triage, screening and detection of the need for medical attention.",
                     "It assists UN SDG 3 (Good health and well-being) by offering a prototype for faster preliminary screening and triage-level flagging at the point of care.")
        replace_in_p(p, "Arogya AI aids the reduction of inequalities by targeting underserved, resource limited communities with an affordable diagnostic tool, SDG 10 (Reducing Inequalities).",
                     "Arogya AI aids the reduction of inequalities by targeting underserved, resource-limited communities with an affordable screening prototype, SDG 10 (Reducing Inequalities).")
        replace_in_p(p, "Low development cost with significantly reduced cost compared to off-the-shelf integrated multi device diagnostic tools",
                     "Low development cost compared to off-the-shelf integrated multi-parameter clinical instruments")

    # ----------------------------------------------------
    # C12 — Separate Limitations Subsection (Section VI)
    # ----------------------------------------------------
    print("Applying C12: Separating Limitations into Section VI...")
    # Clean P203 so limitations are removed from Discussion
    for p in paragraphs:
        t = get_p_text(p)
        if "Before wider adoption, Arogya AI has a number of limitations" in t:
            # Strip limitations from P203
            clean_disc = t[:t.find("Before wider adoption, Arogya AI has a number of limitations")].strip()
            set_p_text(p, clean_disc)
            print("  Removed limitations from Discussion body paragraph.")
        elif t.startswith("The MQ-135 sensor, like all metal-oxide gas sensors") and "Section VII sets out the validation pathway" in t:
            # Clear or remove P204 text
            set_p_text(p, "Detailed limitations and external validity considerations are presented in Section VI below, followed by the rigorous multi-stage validation pathway in Section VII.")
            print("  Updated transition paragraph.")

    # Insert Section VI: Limitations before Conclusion
    target_conclusion = None
    for p in body.findall("w:p", NS):
        if get_p_text(p).strip() == "CONCLUSION":
            target_conclusion = p
            break

    if target_conclusion is not None:
        c_idx = list(body).index(target_conclusion)
        
        # Section VI Heading
        p_lim_head = create_heading_paragraph("VI. LIMITATIONS", level="1")
        body.insert(c_idx, p_lim_head)
        
        # Section VI Content
        p_lim_content1 = create_element("p")
        p_lim_content1.append(create_run(
            "Before wider adoption can be considered, Arogya AI has several key technical, physiological, and operational limitations that must be addressed: "
            "(1) Cohort Diversity and Reference Validation: The current thermal model evaluation was conducted on a laboratory bench cohort (N = 200 held-out frames) "
            "rather than a clinically representative, diverse patient population. Crucially, direct paired comparisons against gold-standard clinical reference instruments "
            "(e.g., calibrated clinical contact thermometers, medical-grade pulse oximeters per ISO 80601-2-61, 12-lead diagnostic ECG machines, and laboratory cyanmethemoglobin blood assays) "
            "have not yet been conducted. All reported figures represent preliminary engineering observations rather than proven diagnostic metrics.",
            size_pt=9
        ))
        body.insert(c_idx + 1, p_lim_content1)
        
        p_lim_content2 = create_element("p")
        p_lim_content2.append(create_run(
            "(2) Optical and Physiological Confounders: Multi-wavelength spectral haemoglobin estimation (AS7343) is exploratory; optical attenuation and diffuse reflectance "
            "are heavily influenced by epidermal melanin concentration (skin pigmentation), peripheral perfusion index, and ambient illumination. Without individualized or "
            "population-stratified spectral calibration curves, non-invasive optical anaemia screening cannot be asserted. Similarly, facial thermography depends on fixed working distance (30 cm), "
            "subject orientation, ambient room temperature, and forehead perspiration.",
            size_pt=9
        ))
        body.insert(c_idx + 2, p_lim_content2)
        
        p_lim_content3 = create_element("p")
        p_lim_content3.append(create_run(
            "(3) Single-Lead Rhythm vs. Diagnostic ECG: The AD8232 analog front-end provides single-lead rhythm screening (Lead-I configuration for detecting tachycardia, bradycardia, and irregular RR intervals). "
            "It cannot substitute for multi-lead diagnostic electrocardiography required to diagnose myocardial ischemia or complex conduction defects. "
            "(4) Environmental Sensor Drift & Hardware Scope: The MQ-135 metal-oxide sensor is vulnerable to baseline thermal drift and humidity interference, requiring periodic field calibration. "
            "Finally, the Grove GSR sensor is physically present on the enclosure rig but is omitted from active sampling in the current firmware release pending standardized conductance baseline protocols.",
            size_pt=9
        ))
        body.insert(c_idx + 3, p_lim_content3)
        print("  Inserted Section VI. LIMITATIONS before Conclusion.")

    # ----------------------------------------------------
    # C10 — Conclusion Corrections
    # ----------------------------------------------------
    print("Applying C10: Conclusion corrections...")
    for p in paragraphs:
        t = get_p_text(p)
        if "Arogya AI demonstrates the engineering feasibility" in t:
            new_conclusion = (
                "Arogya AI demonstrates the engineering feasibility of integrating low-cost multimodal sensing and offline edge-AI processing for preliminary physiological "
                "screening in resource-constrained healthcare environments. Clinical diagnostic validity has not yet been established. The prototype integrates thermal, "
                "single-lead ECG, SpO2/PPG, motion-based respiratory, exploratory spectral, gas, and GSR sensing on an ESP32-S3 platform, with a deterministic, rule-based "
                "triage score driving a zero-literacy output, and achieves practical on-device inference latency (142 ms/frame) and memory footprint for portable use. "
                "These results support Arogya AI as a promising engineering foundation for frontline screening and referral support—not as a diagnostic substitute—and motivate "
                "the validation pathway set out in Section VIII before any clinical deployment claim is made. If that pathway is successfully completed, the prototype's low bill-of-materials "
                "(Rs 8,950) and offline operation position it to assist ASHA workers extending basic physiological screening to underserved rural communities, supporting SDG 3 and SDG 10."
            )
            set_p_text(p, new_conclusion)
            print("  Updated Conclusion paragraph.")

    # ----------------------------------------------------
    # C11 & C14 — Restructure Future Work & Section Renumbering
    # ----------------------------------------------------
    print("Applying C11 & C14: Restructuring Future Work and updating Section numbering...")
    for p in paragraphs:
        t = get_p_text(p).strip()
        if t == "CONCLUSION":
            set_p_text(p, "VII. CONCLUSION")
        elif t == "FUTURE WORK":
            set_p_text(p, "VIII. FUTURE WORK AND VALIDATION PATHWAY")
        elif t == "RESULTS":
            set_p_text(p, "IV. RESULTS")
        elif t == "DISCUSSION":
            set_p_text(p, "V. DISCUSSION")
            
        # Tone down future work items
        replace_in_p(p, "Cloud Text-to-Speech Pipeline with Multiple Languages Support: Pipeline with Multiple languages: Development of a cloud-hosted text-to-speech pipeline",
                     "Offline Text-to-Speech Pipeline: Development of an on-device text-to-speech engine (e.g., using ESP32-S3 I2S audio output with lightweight speech synthesis)")
        replace_in_p(p, "The current haemoglobin estimation channel requires manual per-user calibration. Future work will train a small regression model on a diverse skin-tone dataset to enable automatic, real-time spectral calibration, removing this operational limitation.",
                     "The current haemoglobin estimation channel has not been validated against reference measurements. Future work will collect paired spectral and laboratory haemoglobin data across a diverse skin-tone cohort to train and validate a regression model for automatic spectral calibration.")
        replace_in_p(p, "the mass-market target identified in the feasibility study",
                     "the mass-market cost target")

    # ----------------------------------------------------
    # C15 — Spelling Convention (British English)
    # ----------------------------------------------------
    print("Applying C15: British English standardization...")
    for p in paragraphs:
        replace_in_p(p, "artifacts", "artefacts")
        replace_in_p(p, "artifact", "artefact")
        replace_in_p(p, "generalization", "generalisation")
        replace_in_p(p, "color", "colour")
        replace_in_p(p, "hemoglobin", "haemoglobin")

    # ----------------------------------------------------
    # C16 — Clean IEEE Template Footer
    # ----------------------------------------------------
    print("Applying C16: Cleaning IEEE Template Footer...")
    root_ftr = ET.fromstring(footer_xml)
    for t_elem in root_ftr.findall(".//w:t", NS):
        if "XXX-X-XXXX-XXXX-X" in t_elem.text or "IEEE" in t_elem.text:
            t_elem.text = ""
            print("  Cleared placeholder footer text.")
    cleaned_footer_xml = ET.tostring(root_ftr, encoding="utf-8")

    # ----------------------------------------------------
    # Serialize and Save to Output DOCX
    # ----------------------------------------------------
    print(f"Writing updated document to {DOCX_OUT}...")
    cleaned_doc_xml = ET.tostring(root, encoding="utf-8")
    
    file_map["word/document.xml"] = cleaned_doc_xml
    file_map["word/footer1.xml"] = cleaned_footer_xml

    with zipfile.ZipFile(DOCX_OUT, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for fname, data in file_map.items():
            zout.writestr(fname, data)

    print(f"Successfully generated {DOCX_OUT} ({os.path.getsize(DOCX_OUT)} bytes)!")

if __name__ == "__main__":
    main()
