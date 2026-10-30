"""
Create a professional Word Document (.docx) of README_FIGURES_AND_TABLES.md
with embedded high-resolution figures, styled tables, and publication-ready formatting.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

WORKSPACE_DIR = r"c:\Users\Acer\OneDrive\Desktop\DESKTOP VANSH\Smart Asha"
FIGURES_DIR = os.path.join(WORKSPACE_DIR, "figures")
OUT_DOCX_FIGURES = os.path.join(FIGURES_DIR, "Arogya_AI_Publication_Figures_and_Tables_Dossier.docx")
OUT_DOCX_ROOT = os.path.join(WORKSPACE_DIR, "Arogya_AI_Publication_Figures_and_Tables_Dossier.docx")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:insideV w:val="none"/>'
                        f'<w:left w:val="none"/>'
                        f'<w:right w:val="none"/>'
                        f'</w:tblBorders>')
    tblPr.append(borders)

def make_callout(doc, text_paragraphs, border_color="008080", fill_color="F0F9F8", title=None):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, fill_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
                        f'<w:top w:val="none"/>'
                        f'<w:bottom w:val="none"/>'
                        f'<w:right w:val="none"/>'
                        f'</w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    if title:
        r_title = p.add_run(f"📌 {title}\n")
        r_title.bold = True
        r_title.font.name = "Calibri"
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        
    for i, t in enumerate(text_paragraphs):
        if i > 0 or title:
            p2 = cell.add_paragraph()
            p2.paragraph_format.space_before = Pt(2)
            p2.paragraph_format.space_after = Pt(3)
        else:
            p2 = p
        r = p2.add_run(t)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D) # Navy
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x09, 0x84, 0xE3) # Blue
    return p

def add_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(14)
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.right_indent = Inches(0.2)
    
    # Highlight "Fig. X." in bold
    colon_idx = text.find('.')
    if colon_idx != -1 and colon_idx < 15:
        head = text[:colon_idx+1]
        rest = text[colon_idx+1:]
        r1 = p.add_run(head)
        r1.bold = True
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        
        r2 = p.add_run(rest)
        r2.font.name = "Calibri"
        r2.font.size = Pt(9.0)
        r2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    else:
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

def create_table(doc, headers, data, col_widths=None, alignment=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color="CCCCCC", sz="4", val="single")
    
    # Repeat header row on every page
    header_tr = table.rows[0]._tr.get_or_add_trPr()
    header_tr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    
    # Style Header Row
    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        set_cell_background(cell, "1B365D") # Navy blue
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    # Populate Data Rows
    for row_idx, row_data in enumerate(data):
        row = table.rows[row_idx + 1]
        
        # Don't split row across pages
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        
        bg_color = "F9FBFD" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(row_data):
            cell = row.cells[col_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            p = cell.paragraphs[0]
            if alignment and col_idx < len(alignment):
                p.alignment = alignment[col_idx]
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            
            r = p.add_run(str(val))
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
            
            # Highlight bold if marked
            if str(val).startswith("**") and str(val).endswith("**"):
                r.text = str(val)[2:-2]
                r.bold = True
            elif "COMPLETED" in str(val):
                r.bold = True
                r.font.color.rgb = RGBColor(0x27, 0xAE, 0x60)
                
    # Set column widths if provided
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                if i < len(row.cells):
                    row.cells[i].width = Inches(w)
                    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    return table

def build_dossier():
    print("Initializing Document...")
    doc = docx.Document()
    
    # Set 0.75-inch page margins for a spacious, professional feel
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    # Document Title Block
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("Arogya AI: Publication Figures & Supporting Tables Dossier")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Companion Document to Manuscript Revisions — Comprehensive Resolution of Reviewer Comment 9 & Table 7\n"
                          "IEEE Publication Quality | 300 DPI Renderings | Calibrated Units & Engineering Verifications")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(0x57, 0x60, 0x6F)
    r_sub.italic = True
    
    # Callout Box
    callout_text = [
        "This dossier contains the complete set of 7 publication-grade figures, updated bench observation tables, and reproducible engineering specifications prepared in direct response to the peer review of 'Arogya AI'.",
        "Every figure has been generated at 300 DPI conforming to IEEE transaction styling, eliminating prior discrepancies (e.g. AD8232/14-lead decals, missing axis units, wristband/cloud concepts, and validation ceiling vs test-set accuracy confusion).",
        "Per instructions, the original manuscript file (Arogya_AI_Manuscript_Revised.docx) has remained unrevised, and all revised visual and tabular assets are collated here for author review and submission integration."
    ]
    make_callout(doc, callout_text, border_color="008080", fill_color="F0F9F8", title="Revision Action Compliance Summary")

    # SECTION 1: SUMMARY TABLE
    add_heading_1(doc, "1. Summary of Generated Figures & Revision Alignment")
    
    summary_headers = ["Figure", "Filename", "Key Defect Fixed from Action Plan (Comment 9)", "Status"]
    summary_data = [
        ["Figure 1", "Figure_1_Hardware_Architecture.png", 
         "Table I Alignment: Replaced incorrect ECG references with MAX30003 single-lead SPI front-end. Detailed primary (50 kHz) & secondary (400 kHz) I²C buses, TCA9548A multiplexing (Ports 2, 3, 4, 7), ADC channels (GSR, MQ-135), power subsystem, and dual-core task segregation.", 
         "COMPLETED"],
        ["Figure 2", "Figure_2_Multimodal_Signal_Waveforms.png", 
         "Signal Units & Conditions: Added sampling frequencies (fs), explicit millivolt/intensity/acceleration/conductance units, time window (0–6 s), digital filter specifications, R-peak annotations (RR = 820 ms, 73 bpm), and resting seated bench acquisition context.", 
         "COMPLETED"],
        ["Figure 3", "Figure_3_End_to_End_Architecture.png", 
         "Implemented Prototype Realism: Removed speculative wristband form factor, cloud dashboard, BLE, and buzzer. Replaced with implemented multi-board bench/field kit, Core 0 / Core 1 FreeRTOS tasks, INT8 TFLite Micro inference, and local OLED/LED 3-state output.", 
         "COMPLETED"],
        ["Figure 4", "Figure_4_Operational_Triage_Flowchart.png", 
         "3-State Triage & Persistence: Fully incorporated Green (STABLE), Yellow (REPEAT SCAN), and Red (REFER) states. Added Signal Quality Check (SQC) failure diversion to Yellow, hard safety cut-offs, weighted fusion scoring, and 60-second alert persistence rule.", 
         "COMPLETED"],
        ["Figure 5", "Figure_5_Model_Performance_and_Validation.png", 
         "Inconsistency Resolution (Comment 3): Replaced misleading ~100% accuracy/confidence top bars with a Test-Set Confusion Matrix on the held-out subject-independent test partition (N = 200, 92.4% test accuracy). Retained training/validation learning curves explicitly labeled as small bench validation split.", 
         "COMPLETED"],
        ["Figure 6", "Figure_6_Hardware_Prototype_Architecture.png", 
         "CAD & Physical Prototype Integration: Replaced synthetic block diagram with publication-grade composite featuring: (a) 3D isometric CAD rendering of ergonomic ASA enclosure, (b) 6-axis first-angle orthographic engineering drawings (Drawings 2–7 of Indian Patent Design Registration IDF), and (c) fabricated physical prototype kit (smart_box_box.jpeg) with modular sensor apertures.", 
         "COMPLETED"],
        ["Figure 7", "Figure_7_Thermal_Profiles_Comparison.png", 
         "Thermal Colorbar & Context: Added calibrated temperature colorbar in °C (24.0°C to 39.0°C), pixel row/column indices for the MLX90640 24×32 sensor, explicit ambient conditions (24.2°C, 30 cm distance), and clear non-core-body screening disclaimer.", 
         "COMPLETED"],
    ]
    summary_widths = [0.9, 1.6, 3.6, 0.9]
    summary_align = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    create_table(doc, summary_headers, summary_data, summary_widths, summary_align)

    doc.add_page_break()

    # SECTION 2: PUBLICATION FIGURES & DETAILED CAPTIONS
    add_heading_1(doc, "2. High-Resolution Publication Figures & Manuscript Captions")
    
    figures_info = [
        {
            "num": 1,
            "title": "Figure 1: Hardware Connection Diagram and Bus Architecture",
            "file": "Figure_1_Hardware_Architecture.png",
            "caption": (
                "Fig. 1. Hardware connection diagram and bus architecture of the Arogya AI multimodal edge screening prototype. "
                "The dual-core ESP32-S3 microcontroller coordinates sensor acquisition and TinyML inference across separated bus topologies. "
                "The primary I²C bus (50 kHz) connects through a TCA9548A 8-channel multiplexer to resolve address conflicts across the MPU6050 6-axis IMU (Port 2, 0x68), "
                "MLX90640 far-infrared thermal array (Port 3, 0x33), AS7343 14-channel spectral sensor (Port 4, 0x39), and SSD1306 128×64 OLED display (Port 7, 0x3C). "
                "An isolated secondary I²C bus (400 kHz) handles high-rate optical FIFO transfers from the MAX30102 pulse oximeter. Cardiac rhythm screening is acquired "
                "via SPI through the MAX30003 single-channel biopotential front-end. Analog channels on ESP32-S3 ADC1 capture Grove GSR skin conductance and MQ-135 "
                "ambient air quality. Power is provided by a 3.7 V 2,000 mAh Li-Po battery through a common star ground and dual voltage rails (regulated 3.3 V for sensors "
                "and MCU; boosted 5.0 V for the MQ-135 internal heater)."
            ),
            "width": 6.8
        },
        {
            "num": 2,
            "title": "Figure 2: Synchronous Multimodal Physiological Signal Waveforms",
            "file": "Figure_2_Multimodal_Signal_Waveforms.png",
            "caption": (
                "Fig. 2. Synchronous multimodal physiological waveforms captured by the Arogya AI prototype during a 6-second resting bench acquisition window. "
                "(A) Lead-I single-lead biopotential ECG trace (fs = 250 Hz, 0.5–40 Hz digital bandpass filter) acquired via the MAX30003 front-end from a resting healthy adult volunteer, "
                "illustrating identifiable P-waves, QRS complexes, and T-waves with detected R-peaks (RR = 820 ms, heart rate ≈ 73 bpm). "
                "(B) Photoplethysmogram (PPG, fs = 100 Hz, 5 Hz low-pass filter) from the MAX30102 optical sensor showing clean pulsatile morphology with dicrotic notch (perfusion index = 2.4%, exploratory SpO₂ = 98.2%). "
                "(C) Chest-wall displacement accelerometry (fs = 50 Hz, 0.1–0.5 Hz bandpass filter) derived from the MPU6050 IMU indicating rhythmic respiratory excursions (16.0 breaths/min). "
                "(D) Tonic palmar skin conductance (fs = 10 Hz, 1 Hz low-pass filter) recorded via the Grove GSR sensor (4.62 µS baseline), serving as a low-weight contextual autonomic stress input."
            ),
            "width": 6.8
        },
        {
            "num": 3,
            "title": "Figure 3: End-to-End Operational Architecture & TinyML Edge Pipeline",
            "file": "Figure_3_End_to_End_Architecture.png",
            "caption": (
                "Fig. 3. End-to-end operational architecture and TinyML edge-inference pipeline of the Arogya AI frontline screening system. "
                "The workflow illustrates the implemented multi-board field prototype across four processing stages: (1) Multimodal Sensing Array, comprising facial thermal thermography (MLX90640), "
                "single-lead ECG rhythm screening (MAX30003), pulse oximetry (MAX30102), chest motion (MPU6050), spectral absorption (AS7343), and contextual autonomic/environmental sensing (GSR, MQ-135); "
                "(2) Edge Preprocessing, where Core 0 of the ESP32-S3 manages TCA9548A bus arbitration, digital filtering, 60-second Deep Scan time-domain averaging, and Signal Quality Checks (SQC); "
                "(3) On-Device AI Inference, where Core 1 executes an INT8 post-training quantized CNN for thermal pattern recognition (142 ms latency, 232 KB PSRAM) and deterministic sub-score normalization "
                "with weighted multi-sensor fusion; and (4) Local Zero-Cloud Output, providing offline triaging via an SSD1306 OLED numeric display and an intuitive two-colour visual LED indicator (Green: STABLE, Blinking Red: REPEAT SCAN, Solid Red: REFER)."
            ),
            "width": 6.8
        },
        {
            "num": 4,
            "title": "Figure 4: Operational Flowchart for 60-Second Deep Scan & Three-State Triage",
            "file": "Figure_4_Operational_Triage_Flowchart.png",
            "caption": (
                "Fig. 4. Operational flowchart of the 60-second Deep Scan acquisition and three-state triage decision logic. "
                "Following sensor positioning verification in the Idle State, the operator triggers the 60-second Deep Scan. Incoming signals pass through an automated Signal Quality Check (thermal variance, "
                "PPG perfusion index > 0.5%, and ECG lead-contact baseline). If quality checks fail, the system diverts to the Yellow State (REPEAT SCAN), signaling the operator via a blinking red LED and an OLED "
                "prompt to reposition the probes. Valid signals undergo INT8 CNN thermal inference and algorithmic feature extraction. If any vital parameter crosses an extreme emergency cut-off "
                "(e.g., SpO₂ < 85%, heart rate < 40 or > 150 bpm) and persists for the 60-second duration, the system latches directly to the Red State (REFER). Otherwise, normalized bounded sub-scores (s_p in [0, 1]) "
                "are fused into a weighted composite Triage Score. Thresholds tau_1 = 0.30 and tau_2 = 0.65 partition outcomes into Green (STABLE), Yellow (REPEAT SCAN), and Red (REFER). Single-reading transient spikes are suppressed by the 60-second alert persistence rule."
            ),
            "width": 6.8
        },
        {
            "num": 5,
            "title": "Figure 5: Model Performance: Test Confusion Matrix & Validation Curves",
            "file": "Figure_5_Model_Performance_and_Validation.png",
            "caption": (
                "Fig. 5. Thermal fever screening model performance: (A) test-set confusion matrix on the held-out subject-independent test partition (92.4% accuracy), and (B) training loss and validation accuracy curves over 30 epochs. "
                "(A) Confusion matrix on the held-out subject-independent test partition (N = 200 frames from subjects completely unobserved during training), demonstrating a test classification accuracy of 92.5%, sensitivity of 91.0% [95% CI: 83.6%–95.8%], "
                "specificity of 94.0% [95% CI: 87.4%–97.8%], precision of 93.8% [95% CI: 87.0%–97.7%], and balanced accuracy of 92.5% (F1-score: 92.4%). "
                "(B) Categorical cross-entropy loss and classification accuracy across 30 training epochs. Validation accuracy approaches ceiling (~98.8%–100%) and validation loss reaches ~0.11 as an expected artifact of the small bench validation cohort size; "
                "the 92.4% held-out test metric in Panel A reflects genuine subject-independent generalization."
            ),
            "width": 6.8
        },
        {
            "num": 6,
            "title": "Figure 6: 3D CAD Enclosure Model, Orthographic Views & Physical Prototype",
            "file": "Figure_6_Hardware_Prototype_Architecture.png",
            "caption": (
                "Fig. 6. Arogya AI frontline screening workstation: (a) 3D isometric CAD rendering of ergonomic handheld enclosure "
                "(medical-grade ASA polymer, 210 × 125 × 45 mm, <450 g) with integrated carry handle, 128×64 OLED display window, tactile controls, and lateral sensor jacks; "
                "(b) Multi-view first-angle orthographic CAD drawings (Drawings 2–7 of Indian Patent Design Registration IDF) covering front elevation, top plan view, "
                "left biosensor inputs (Lead-I ECG, SpO2, GSR), right I/O & charging interfaces (USB-C, HDMI, RJ45, DC power), rear ventilation grille and battery service bay, "
                "and bottom anti-skid silicone feet; (c) Fabricated physical hardware prototype bench kit (smart_box_box.jpeg) validated in on-device testing with healthy volunteers."
            ),
            "width": 6.8
        },
        {
            "num": 7,
            "title": "Figure 7: Comparative Thermal Profiles with Calibrated Temperature Scale",
            "file": "Figure_7_Thermal_Profiles_Comparison.png",
            "caption": (
                "Fig. 7. Illustrative comparative facial thermal profiles captured by the MLX90640 24×32 far-infrared sensor: (A) healthy baseline profile with uniform surface temperature distribution, and (B) febrile profile exhibiting elevated frontal/temporal thermal patterns. "
                "Thermal matrices were captured at a standardized 30 cm subject-to-sensor distance under controlled ambient laboratory conditions (Tamb = 24.2 °C, relative humidity = 50%, surface emissivity epsilon = 0.98). "
                "(A) Healthy subject profile showing uniform facial heat distribution with forehead surface temperature ranging from 33.5 °C to 35.5 °C (mean: 34.4 °C, peak: 35.5 °C; TFLite INT8 CNN inference: Normal, confidence = 0.94, triage sub-score = 0.08). "
                "(B) Febrile subject profile exhibiting pronounced bilateral frontal and temporal hyperthermia (36.8 °C to 38.7 °C, peak: 38.7 °C, mean: 37.6 °C; TFLite INT8 CNN inference: Elevated Thermal Pattern, confidence = 0.91, triage sub-score = 0.92). "
                "Calibrated temperature colorbar scale spans 24.0 °C to 39.0 °C. "
                "Note: Forehead skin-surface thermography is presented as an illustrative preliminary screening indicator and is not equivalent to core-body diagnostic thermometry."
            ),
            "width": 6.8
        }
    ]

    for fig_item in figures_info:
        add_heading_2(doc, fig_item["title"])
        img_path = os.path.join(FIGURES_DIR, fig_item["file"])
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(4)
            run_img = p_img.add_run()
            run_img.add_picture(img_path, width=Inches(fig_item["width"]))
            add_caption(doc, fig_item["caption"])
        else:
            print(f"Warning: Image file not found: {img_path}")
            
        doc.add_page_break()

    # SECTION 3: ACCOMPANYING PUBLICATION TABLES
    add_heading_1(doc, "3. Accompanying Publication Tables ('etc')")
    
    # Table II (Revised)
    add_heading_2(doc, "TABLE II (REVISED): Preliminary Bench Observations Across Major Sensing Modules")
    p_t2_desc = doc.add_paragraph()
    r_t2 = p_t2_desc.add_run("Fully relabeled per Reviewer Comments 4 and 9 to include sample sizes (n), physical units, measurement conditions, and reference comparison status.")
    r_t2.italic = True
    r_t2.font.color.rgb = RGBColor(0x57, 0x60, 0x6F)
    
    t2_headers = ["Sensing Subsystem", "Transducer / IC", "Parameter Measured", "Engineering Observation (n Bench Captures)", "Measurement Conditions", "Reference Comparison Status"]
    t2_data = [
        ["Surface Temperature Screening", "MLX90640 (24×32)", "Facial surface thermal distribution & peak temp", "Detects localized facial temperature elevation (n = 200 test frames)", "Controlled lab bench, Tamb = 24.2 °C, 30 cm distance, emissivity ε = 0.98", "Reference clinical thermometer comparison pending (Section VII validation pathway)"],
        ["Single-Lead Rhythm Screening", "MAX30003", "R-R interval & heart rate variability flag", "Clear QRS complexes; flags tachycardia, bradycardia & irregular beat spacing (n = 15 recordings)", "Resting seated adult volunteer, Lead-I electrode configuration, 0.5–40 Hz bandpass", "Screening only; not equivalent to 12-lead diagnostic ECG"],
        ["Pulse Oximetry (Exploratory)", "MAX30102", "Optical PPG pulse wave & exploratory SpO₂", "Stable pulsatile signal with dicrotic notch at perfusion index > 0.5% (n = 15 recordings)", "Static finger placement, indoor ambient lighting", "Exploratory; benchmark comparison per ISO 80601-2-61 required"],
        ["Motion-Derived Respiration", "MPU6050", "Chest-wall displacement acceleration", "Rhythmic signal tracking resting respiration (14–18 bpm, n = 15 recordings)", "Sensor placed on sternum/chest, resting seated, 0.1–0.5 Hz bandpass", "Exploratory; comparison with spirometer / capnography pending"],
        ["Autonomic Stress Context", "Grove GSR", "Palmar skin conductance", "Tonic baseline ~4.2–4.8 µS; detectable conductance drop upon stimulus (n = 10 runs)", "Bipolar dry electrodes on index and middle fingers", "Contextual indicator only; no independent diagnostic cut-off"],
        ["Ambient Air Quality Context", "MQ-135", "Environmental VOC / air quality proxy", "Detects relative indoor air quality shifts (n = 10 bench runs)", "Indoor laboratory bench, 48 h pre-heated sensor coil", "Contextual flag only; prone to drift; does not affect clinical score directly"],
        ["Multi-Spectral Hb (Exploratory)", "AS7343 (14-Ch)", "Multi-wavelength optical absorption ratio", "Exploratory multi-band reflection signature (n = 10 bench captures)", "Contact finger reflectance under controlled LED illumination", "Exploratory only; uncalibrated; requires laboratory cyanmethemoglobin benchmarking"]
    ]
    t2_widths = [1.2, 1.0, 1.1, 1.2, 1.2, 1.1]
    create_table(doc, t2_headers, t2_data, t2_widths)

    doc.add_page_break()

    # Table IV (New)
    add_heading_2(doc, "TABLE IV (NEW): Held-Out Test Set Evaluation Metrics with 95% Confidence Intervals")
    p_t4_desc = doc.add_paragraph()
    r_t4 = p_t4_desc.add_run("Directly resolves Reviewer Comments 2, 3, and 9. Evaluated on the held-out subject-independent test partition (N = 200).")
    r_t4.italic = True
    r_t4.font.color.rgb = RGBColor(0x57, 0x60, 0x6F)
    
    t4_headers = ["Metric", "Formula / Method", "Value on Held-Out Test Set (N = 200)", "95% Confidence Interval (Wilson Score Method)"]
    t4_data = [
        ["Overall Classification Accuracy", "(TP + TN) / (TP + TN + FP + FN)", "**92.5%**", "88.0% – 95.8%"],
        ["Clinical Sensitivity (Recall)", "TP / (TP + FN)", "**91.0%**", "83.6% – 95.8%"],
        ["Clinical Specificity (TNR)", "TN / (TN + FP)", "**94.0%**", "87.4% – 97.8%"],
        ["Positive Predictive Value (Precision)", "TP / (TP + FP)", "**93.8%**", "87.0% – 97.7%"],
        ["Negative Predictive Value (NPV)", "TN / (TN + FN)", "**91.3%**", "84.2% – 95.9%"],
        ["Balanced Accuracy", "(Sensitivity + Specificity) / 2", "**92.5%**", "87.5% – 95.8%"],
        ["F1-Score", "2 · (Precision · Sensitivity) / (Precision + Sensitivity)", "**92.4%**", "Bootstrap CI: 86.8% – 95.5%"]
    ]
    t4_widths = [1.8, 2.0, 1.4, 1.6]
    t4_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    create_table(doc, t4_headers, t4_data, t4_widths, t4_align)

    # Table V (New)
    add_heading_2(doc, "TABLE V (NEW): Hardware Configuration, Software Versions & Sampling Parameters")
    p_t5_desc = doc.add_paragraph()
    r_t5 = p_t5_desc.add_run("Directly resolves Reviewer Comments 7, 9, and Table 5 of the Revision Action Document.")
    r_t5.italic = True
    r_t5.font.color.rgb = RGBColor(0x57, 0x60, 0x6F)
    
    t5_headers = ["Subsystem / Parameter", "Implementation Specification", "Operational Notes"]
    t5_data = [
        ["Processor Platform", "Espressif ESP32-S3-WROOM-1", "Dual-core Xtensa LX7 @ 240 MHz, 512 KB SRAM, 8 MB Octal PSRAM, 16 MB SPI Flash"],
        ["Firmware & RTOS", "ESP-IDF v5.1.2 with FreeRTOS", "Dual-core pinned tasks: Core 0 (Sensor acquisition & filtering), Core 1 (TinyML & fusion)"],
        ["TinyML Framework", "TensorFlow Lite for Microcontrollers (TFLite Micro v2.4.0)", "INT8 post-training quantization, 232 KB external PSRAM tensor arena, 142 ms inference latency"],
        ["Primary I²C Bus", "GPIO 8 (SDA) / GPIO 18 (SCL) @ 50 kHz", "Clock throttled to 50 kHz for line capacitance tolerance across multiplexer cable lines"],
        ["I²C Multiplexer", "TI TCA9548A (Address: 0x70)", "Resolves bus conflicts; channels: MPU6050 (CH2), MLX90640 (CH3), AS7343 (CH4), OLED (CH7)"],
        ["Secondary Isolated I²C Bus", "GPIO 16 (SDA) / GPIO 17 (SCL) @ 400 kHz", "Direct connection to MAX30102 optical sensor to avoid FIFO buffer overflow"],
        ["SPI Interface", "GPIO 11 (MOSI), GPIO 13 (MISO), GPIO 12 (SCLK), GPIO 10 (CS)", "Dedicated high-speed SPI bus for MAX30003 single-lead ECG front-end"],
        ["Analog ADC Channels", "ESP32-S3 ADC1 (GPIO 4: GSR, GPIO 6: MQ-135)", "12-bit resolution (0–4095), eFuse factory-calibrated reference voltage (Vref = 1100 mV)"],
        ["Sampling Rates (fs)", "• MAX30003 ECG: 250 Hz\n• MAX30102 PPG: 100 Hz\n• MPU6050 IMU: 50 Hz\n• MLX90640 Thermal: 2–4 Hz\n• Grove GSR: 10 Hz\n• MQ-135 Gas: 1 Hz", "Synchronized across FreeRTOS sensor queue; 60-second acquisition window generates stable averages"],
        ["Power Management", "3.7 V 2,000 mAh Single-Cell Li-Po with TP4056 USB-C Charging", "Active with AI: 185 mA (10.8 h calculated runtime); Standby: 12 mA (6.9 days calculated runtime)"]
    ]
    t5_widths = [1.8, 2.3, 2.7]
    create_table(doc, t5_headers, t5_data, t5_widths)

    doc.add_page_break()

    # Table VI (New)
    add_heading_2(doc, "TABLE VI (NEW): Deterministic Sensor Fusion Parameters, Weights, and Quality Gates")
    p_t6_desc = doc.add_paragraph()
    r_t6 = p_t6_desc.add_run("Directly resolves Reviewer Comments 5, 6, and Table 6 of the Revision Action Document.")
    r_t6.italic = True
    r_t6.font.color.rgb = RGBColor(0x57, 0x60, 0x6F)
    
    t6_headers = ["Parameter p", "Normal Range [low_p, high_p]", "Outer Risk Bounds [out_low_p, out_high_p]", "Prior Weight w_p", "Signal Quality Check (SQC) Gate", "Hard Critical Safety Cut-Off"]
    t6_data = [
        ["Forehead Surface Temp", "33.0 °C – 36.0 °C", "< 31.0 °C or > 38.5 °C", "**0.30**", "Thermal frame variance > 0.25 (non-occluded)", "> 39.5 °C (Immediate Red)"],
        ["Exploratory SpO₂", "95% – 100%", "< 90%", "**0.25**", "Optical Perfusion Index (PI) > 0.5%", "< 85% (Immediate Red)"],
        ["Heart Rate / ECG Rhythm", "60 – 100 bpm", "< 50 bpm or > 120 bpm", "**0.20**", "Lead-off contact check & noise floor < 0.1 mV", "< 40 or > 150 bpm (Immediate Red)"],
        ["Respiration Rate (IMU)", "12 – 20 breaths/min", "< 8 or > 28 breaths/min", "**0.15**", "Motion artifact envelope check", "< 6 or > 32 bpm (Immediate Red)"],
        ["Skin Conductance (GSR)", "2.0 – 8.0 µS", "< 1.0 µS or > 15.0 µS", "**0.10**", "Electrode contact resistance check", "None (Contextual only)"],
        ["Multi-Spectral Hb Index", "Exploratory baseline", "N/A", "**0.00**", "Optical reflectance intensity validation", "None (Exploratory only)"],
        ["Ambient Gas (MQ-135)", "Baseline air", "Elevated VOC context", "**0.00**", "Sensor warm-up time >= 120 s", "None (Environmental flag only)"]
    ]
    t6_widths = [1.4, 1.2, 1.2, 0.7, 1.3, 1.0]
    t6_align = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    create_table(doc, t6_headers, t6_data, t6_widths, t6_align)

    # Triage decision logic summary
    triage_notes = [
        "Composite Triage Scoring Formula: Score = Sum(w_p * s_p) / Sum(w_p), evaluated strictly over sensing channels that satisfy their respective Signal Quality Check (SQC) criteria.",
        "GREEN (STABLE): Composite Score < 0.30 and all required channels pass SQC. Indicated by a steady Green LED and 'STABLE' display on the SSD1306 OLED.",
        "YELLOW (REPEAT SCAN): 0.30 <= Composite Score < 0.65 OR any required channel fails its SQC. Indicated by a blinking Red LED and 'REPEAT SCAN' prompt on the OLED.",
        "RED (REFER): Composite Score >= 0.65 OR any vital parameter crosses its hard critical safety threshold. Indicated by a steady Red LED and 'REFER' escalation notice on the OLED.",
        "60-Second Alert Persistence Rule: State transitions to Yellow or Red are latched only after remaining sustained across the full 60-second Deep Scan acquisition window to eliminate single-sample transient false alarms."
    ]
    make_callout(doc, triage_notes, border_color="E67E22", fill_color="FEF9E7", title="Deterministic Triage Decision & State Transition Rules")

    # Save to both target locations
    print(f"Saving Document to:\n1. {OUT_DOCX_FIGURES}")
    doc.save(OUT_DOCX_FIGURES)
    print(f"Saved: {OUT_DOCX_FIGURES}")
    
    print(f"2. {OUT_DOCX_ROOT}")
    try:
        doc.save(OUT_DOCX_ROOT)
        print(f"Saved: {OUT_DOCX_ROOT}")
    except PermissionError:
        print(f"Notice: {OUT_DOCX_ROOT} is currently open in Microsoft Word. Saved to figures directory.")
    print("SUCCESS! Dossier document successfully created and saved.")

if __name__ == "__main__":
    build_dossier()
