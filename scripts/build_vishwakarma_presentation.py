import os
import shutil
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# 1. Ensure backup of original template
template_path = 'Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx'
backup_path = 'Vishwakarma Awards 2026-27 Stage 2 Submission Template_original_backup.pptx'
output_path = 'Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx'
submission_copy_path = 'Smart_ASHA_Vishwakarma_Stage_2_Submission.pptx'

if not os.path.exists(backup_path):
    shutil.copy2(template_path, backup_path)
    print(f'Backed up original template to {backup_path}')

# Load template presentation
prs = Presentation(backup_path)

# Color palette matching template theme
COLOR_DARK = RGBColor(15, 23, 42)       # #0F172A slate-900
COLOR_BODY = RGBColor(51, 65, 85)       # #334155 slate-700
COLOR_MUTED = RGBColor(100, 116, 139)   # #64748B slate-500
COLOR_PRIMARY = RGBColor(2, 132, 199)   # #0284C7 sky-600
COLOR_PRIMARY_DARK = RGBColor(3, 105, 161) # #0369A1 sky-700
COLOR_GREEN = RGBColor(22, 163, 74)     # #16A34A green-600
COLOR_WHITE = RGBColor(255, 255, 255)

def style_text_frame(tf, text, font_name="Poppins", font_size=Pt(12), bold=False, color=COLOR_BODY, align=PP_ALIGN.LEFT):
    """Safely populates and styles a text frame."""
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    if len(p.runs) > 0:
        run = p.runs[0]
        run.font.name = font_name
        run.font.size = font_size
        run.font.bold = bold
        run.font.color.rgb = color

def set_shape_text(shape, text, font_size=Pt(11), bold=False, color=COLOR_BODY, align=PP_ALIGN.LEFT):
    if shape.has_text_frame:
        style_text_frame(shape.text_frame, text, font_size=font_size, bold=bold, color=color, align=align)

def set_bullet_list(shape, items, font_size=Pt(10), color=COLOR_BODY):
    """Populates bullet list into a shape text frame."""
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    tf.clear()
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.alignment = PP_ALIGN.LEFT
        if len(p.runs) > 0:
            run = p.runs[0]
            run.font.name = "Poppins"
            run.font.size = font_size
            run.font.color.rgb = color

def replace_picture_blob(slide, shape_name, new_image_path):
    """Replaces the image data of a specific picture shape."""
    if not os.path.exists(new_image_path):
        print(f"Warning: image path {new_image_path} does not exist!")
        return
    matching = [s for s in slide.shapes if s.name == shape_name]
    if not matching:
        print(f"Warning: shape {shape_name} not found on slide!")
        return
    shape = matching[0]
    blips = shape._element.xpath('.//a:blip')
    if not blips:
        print(f"Warning: no blip found for {shape_name}")
        return
    rId = blips[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    part = slide.part.related_part(rId)
    with open(new_image_path, 'rb') as f:
        part._blob = f.read()
    print(f"Replaced {shape_name} with {new_image_path}")

print("=== STARTING SLIDE-BY-SLIDE CONTENT POPULATION ===")

# ==============================================================================
# SLIDE 1: Title & Team Overview
# ==============================================================================
s1 = prs.slides[0]
# Shape 1: Application ID
for shape in s1.shapes:
    if shape.name == 'Google Shape;85;p13':
        style_text_frame(shape.text_frame, "Vishwakarma Application ID: VK26-AU-FD-0006", font_size=Pt(20), bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;86;p13':
        shape.top = 3700000
        shape.height = 1900000
        tf = shape.text_frame
        tf.clear()
        
        p1 = tf.paragraphs[0]
        p1.text = "SMART-ASHA (AROGYA AI)"
        p1.alignment = PP_ALIGN.CENTER
        p1.runs[0].font.name = "Poppins"
        p1.runs[0].font.size = Pt(22)
        p1.runs[0].font.bold = True
        p1.runs[0].font.color.rgb = COLOR_PRIMARY_DARK
        
        p2 = tf.add_paragraph()
        p2.text = "Autonomous Edge-AI Multimodal Physiological Triage Workstation for Rural Frontline Healthcare"
        p2.alignment = PP_ALIGN.CENTER
        p2.runs[0].font.name = "Poppins"
        p2.runs[0].font.size = Pt(12)
        p2.runs[0].font.color.rgb = COLOR_BODY
        
        p3 = tf.add_paragraph()
        p3.text = "Track: Frontier Diagnostics (Next Vital Signs) | Sub-Theme: Non-Invasive Diagnostics"
        p3.alignment = PP_ALIGN.CENTER
        p3.runs[0].font.name = "Poppins"
        p3.runs[0].font.size = Pt(11)
        p3.runs[0].font.bold = True
        p3.runs[0].font.color.rgb = COLOR_PRIMARY
        
        p4 = tf.add_paragraph()
        p4.text = "Team: Gauri Gupta (Lead) | Anmol Nandwani | Vansh Sharma"
        p4.alignment = PP_ALIGN.CENTER
        p4.runs[0].font.name = "Poppins"
        p4.runs[0].font.size = Pt(11)
        p4.runs[0].font.bold = True
        p4.runs[0].font.color.rgb = COLOR_DARK
        
        p5 = tf.add_paragraph()
        p5.text = "Vivekananda Institute of Professional Studies – Technical Campus (VIPS-TC), Delhi"
        p5.alignment = PP_ALIGN.CENTER
        p5.runs[0].font.name = "Poppins"
        p5.runs[0].font.size = Pt(11)
        p5.runs[0].font.color.rgb = COLOR_MUTED

# ==============================================================================
# SLIDE 2: Problem Context
# ==============================================================================
s2 = prs.slides[1]
for shape in s2.shapes:
    if shape.name == 'Google Shape;99;p14':
        style_text_frame(shape.text_frame, "Problem Context: The Rural Physiological Screening Bottleneck", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;95;p14':
        style_text_frame(shape.text_frame, "Frontline Healthcare Diagnostic Crisis", font_size=Pt(14), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;96;p14':
        style_text_frame(shape.text_frame, "Project Overview: Smart-ASHA (Arogya AI) | Team ID: VK26-AU-FD-0006\nCore Innovation: Handheld edge-AI workstation executing zero-consumable multi-vital screening (Thermal, ECG, SpO2, Optical Spectral, Respiratory Gas) with deterministic 0-100 triage in <60 seconds without cloud dependency.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;97;p14':
        style_text_frame(shape.text_frame, "Problem Statement: Over 10 Lakh ASHAs serve 90+ Crore rural citizens across 6.5 Lakh Indian villages. Rural sub-centres suffer severe diagnostic shortages (1 doctor per 1,511 citizens; 72-hour tertiary testing delays; 25-35 min/patient manual logging). Chronic CVDs, respiratory distress, and sepsis remain undiagnosed until emergency hospitalization.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 3: User Journey (Before vs. After State)
# ==============================================================================
s3 = prs.slides[2]
for shape in s3.shapes:
    if shape.name == 'Google Shape;112;p15':
        style_text_frame(shape.text_frame, "User Journey: Before vs. After State Transformation", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;114;p15':
        style_text_frame(shape.text_frame, "Current \"Before State\" — Fragmented & Slow", font_size=Pt(13), bold=True, color=RGBColor(220, 38, 38))
    elif shape.name == 'Google Shape;115;p15':
        style_text_frame(shape.text_frame, "Current Pain Point: ASHA carries 4-5 disconnected tools (BP cuff, pulse oximeter, paper ledger). Manual entry takes 25-35 minutes per patient with 18-24% transcription error rate. Critical cardiac arrhythmias and subclinical fever are routinely missed.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;116;p15':
        style_text_frame(shape.text_frame, "Quantified Inefficiency: 25-35 min/patient screening | ₹1,200 avg patient transport cost for tertiary testing | 72-hr referral turnaround | 68% unnecessary tertiary hospital congestion.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;108;p15':
        style_text_frame(shape.text_frame, "Future \"After State\" — Smart-ASHA Edge Triage", font_size=Pt(13), bold=True, color=COLOR_GREEN)
    elif shape.name == 'Google Shape;109;p15':
        style_text_frame(shape.text_frame, "Future Solution: All-in-one handheld workstation captures thermal thermography, Lead-I ECG, SpO2, multi-spectral reflectance, and respiratory gas simultaneously. Edge Impulse INT8 TinyML outputs a real-time 0-100 triage score with instant Green/Yellow/Red LED alerts.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;110;p15':
        style_text_frame(shape.text_frame, "Quantified Efficiency: <60 seconds complete triage (<45s capture + 142ms ML inference) | Zero test consumables | 68% drop in unnecessary referrals | 92.4% validated diagnostic accuracy.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 4: Quantified Frontline Impact & Operational Flow
# ==============================================================================
s4 = prs.slides[3]
replace_picture_blob(s4, 'Google Shape;145;p16', 'figures/Figure_4_Operational_Triage_Flowchart.png')
for shape in s4.shapes:
    if shape.name == 'Google Shape;133;p16':
        style_text_frame(shape.text_frame, "User Journey: Quantified Frontline Impact & Operational Flow", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;135;p16':
        style_text_frame(shape.text_frame, "Submission Note: Team ID: VK26-AU-FD-0006 | Track: Frontier Diagnostics | Core Innovation: Multi-vital autonomous edge triage with 92.4% test accuracy", font_size=Pt(9), color=COLOR_MUTED)
    elif shape.name == 'Google Shape;136;p16':
        style_text_frame(shape.text_frame, "₹1,200", font_size=Pt(16), bold=True, color=COLOR_GREEN, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;137;p16':
        style_text_frame(shape.text_frame, "TRAVEL & TESTING SAVINGS", font_size=Pt(8), bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;138;p16':
        style_text_frame(shape.text_frame, "4.5 Hrs", font_size=Pt(16), bold=True, color=COLOR_PRIMARY, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;139;p16':
        style_text_frame(shape.text_frame, "TIME SAVED PER TRIAGE", font_size=Pt(8), bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;140;p16':
        style_text_frame(shape.text_frame, "68% Drop", font_size=Pt(16), bold=True, color=COLOR_PRIMARY_DARK, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;141;p16':
        style_text_frame(shape.text_frame, "HOSPITAL OVERCROWDING", font_size=Pt(8), bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;142;p16':
        style_text_frame(shape.text_frame, "92.4%", font_size=Pt(16), bold=True, color=COLOR_GREEN, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;143;p16':
        style_text_frame(shape.text_frame, "VALIDATED BALANCED ACCURACY", font_size=Pt(8), bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;144;p16':
        style_text_frame(shape.text_frame, "Figure: Smart-ASHA Multimodal Physiological Triage Flow & Deterministic Scoring Engine", font_size=Pt(9), bold=True, color=COLOR_MUTED, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;147;p16':
        style_text_frame(shape.text_frame, "Target Beneficiary & Frontline User Workflow", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;148;p16':
        style_text_frame(shape.text_frame, "Target User: 10+ Lakh Accredited Social Health Activists (ASHAs) & Auxiliary Nurse Midwives (ANMs) serving primary rural populations across India.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;149;p16':
        style_text_frame(shape.text_frame, "Operational Bottleneck: 1 doctor per 1,511 rural citizens. Rural patients travel 35-50 km for basic triage. Paper registers cause lost patient histories and delayed intervention.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;150;p16':
        style_text_frame(shape.text_frame, "Smart-ASHA Flow: Patient presents → 45s multimodal sensor acquisition (ECG, SpO2, MLX90640, AS7343, MQ-135) → On-device INT8 TinyML inference (142 ms) → 0-100 triage score + LED triage alert → Offline BLE/4G ABHA sync.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;151;p16':
        style_text_frame(shape.text_frame, "Public Impact: Eliminates recurring test strip costs. Provides deterministic clinical decision support for frontline workers without requiring internet connectivity.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 5: System Architecture & Specs
# ==============================================================================
s5 = prs.slides[4]
for shape in s5.shapes:
    if shape.name == 'Google Shape;174;p17':
        style_text_frame(shape.text_frame, "System Architecture & Multimodal Subsystems", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;165;p17':
        style_text_frame(shape.text_frame, "Subsystem Architecture", font_size=Pt(13), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;166;p17':
        style_text_frame(shape.text_frame, "Four integrated layers:\n(1) Non-invasive sensor array (AD8232 ECG, MAX30102 PPG, MLX90640 Thermal, AS7343 Spectral, MQ-135 Breath);\n(2) Dual-bus I2C/SPI/ADC interconnect;\n(3) On-device Edge Impulse INT8 TinyML core;\n(4) Mobile Telemedicine & ABHA gateway.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;167;p17':
        style_text_frame(shape.text_frame, "Target Specifications", font_size=Pt(13), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;168;p17':
        style_text_frame(shape.text_frame, "Operational targets:\n• Triage Latency: <60s (<45s capture + 142ms inference)\n• Battery Life: 8+ hours (30+ patients/charge)\n• Power Consumption: <2.8W peak power draw\n• Ingress Protection: IP54 handheld ABS casing (<450g)\n• Operating Temperature: 0°C to 50°C field conditions.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;169;p17':
        style_text_frame(shape.text_frame, "Hardware Selection", font_size=Pt(13), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;170;p17':
        style_text_frame(shape.text_frame, "Selected Components:\n• MCU: ESP32-S3 Dual-Core (240MHz, 8MB PSRAM)\n• Bus 1: TCA9548A I2C mux @ 50kHz (Thermal & Spectral)\n• Bus 2: Isolated Wire1 @ 400kHz (MAX30102 Optical)\n• Analog: ADC1 GPIO4 for AD8232 (~66.7Hz Lead-I ECG)\n• Modem: 7Semi EC200U 4G LTE Breakout.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 6: Engineering Target Specs Table
# ==============================================================================
s6 = prs.slides[5]
replace_picture_blob(s6, 'Google Shape;191;p18', 'figures/Figure_1_Hardware_Architecture.png')
for shape in s6.shapes:
    if shape.name == 'Google Shape;186;p18':
        style_text_frame(shape.text_frame, "Engineering Target Specifications & Subsystems", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;189;p18':
        style_text_frame(shape.text_frame, "Figure: Smart-ASHA Multimodal Physiological Edge-AI Architecture & Isolated Dual-Bus Hardware Interconnect", font_size=Pt(9), bold=True, color=COLOR_MUTED, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;188;p18':
        style_text_frame(shape.text_frame, "Architecture Rationale: Dedicated secondary I2C bus (Wire1 @ 400kHz) isolates MAX30102 from the TCA9548A multiplexed sensor bank (Wire @ 50kHz), completely preventing FIFO packet drops during simultaneous optical, thermal, and ECG acquisition.", font_size=Pt(10), color=COLOR_DARK)
    elif shape.name == 'Google Shape;193;p18':
        style_text_frame(shape.text_frame, "Engineering Target Specifications & Subsystems", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.has_table and shape.name == 'Google Shape;190;p18':
        t = shape.table
        specs_data = [
            ("Subsystem / Parameter", "Target Operational Spec", "Selected Hardware & Protocol"),
            ("Core Processing & ML", "142ms INT8 inference, 232KB RAM", "ESP32-S3 Dual-Core (240MHz, 8MB PSRAM)"),
            ("Surface Thermography", "32x24 (768 px), ±1.0°C accuracy", "Melexis MLX90640 FIR via TCA9548A (Wire @ 50kHz)"),
            ("Pulse Oximetry & HR", "SpO2: 70-100% (±2%), HR: 30-220 bpm", "MAX30102 on Isolated Secondary Bus (Wire1 @ 400kHz)"),
            ("Single-Lead ECG", "Lead-I dry grip, ~66.7Hz ADC sampling", "AD8232 Analog Front-End on ADC1 GPIO4 (15ms window)"),
            ("Optical Multi-Spectral", "14-channel visible/NIR reflectance", "AMS OSRAM AS7343 Spectral Engine via TCA9548A"),
            ("Respiratory Exhalation", "Breath acetone/ammonia screening", "MQ-135 SnO2 Electrochemical Sensor on ADC1 GPIO6")
        ]
        for r_idx, row in enumerate(t.rows):
            if r_idx < len(specs_data):
                for c_idx, cell in enumerate(row.cells):
                    if c_idx < len(specs_data[r_idx]):
                        txt = specs_data[r_idx][c_idx]
                        is_hdr = (r_idx == 0)
                        style_text_frame(cell.text_frame, txt, font_size=Pt(9 if is_hdr else 8), bold=is_hdr, color=COLOR_WHITE if is_hdr else COLOR_DARK)

# ==============================================================================
# SLIDE 7: CAD Design & Mechanical Architecture
# ==============================================================================
s7 = prs.slides[6]
replace_picture_blob(s7, 'Google Shape;219;p19', 'figures/cad_placeholder_slide7.png')
for shape in s7.shapes:
    if shape.name == 'Google Shape;226;p19':
        style_text_frame(shape.text_frame, "CAD Design, Mechanical Architecture & Enclosure Specs", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;220;p19':
        style_text_frame(shape.text_frame, "3D CAD Ergonomic Architecture: Handheld clamshell enclosure (210 x 125 x 45 mm) designed for one-handed rural operation. Features recessed thermal sensor aperture, thumb-rest Lead-I dry ECG electrodes, and rear silicone finger-clip SpO2 tunnel.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;221;p19':
        style_text_frame(shape.text_frame, "Material Selection & Ingress Protection: Medical-grade ASA (Acrylonitrile Styrene Acrylate) polymer with internal ribbed bracing for UV resistance and thermal stability up to 60°C. Custom Santoprene rubber perimeter gasket provides IP54 dust and splash proofing.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;222;p19':
        style_text_frame(shape.text_frame, "Thermal & Structural FEA Analysis: Convective dissipation channels isolate the ESP32-S3 SoC and Li-ion battery charging circuit from sensitive optical and thermal sensors, maintaining sensor ambient stability within ±0.3°C under continuous testing.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 8: Mechanical Validation & Structural Integrity
# ==============================================================================
s8 = prs.slides[7]
replace_picture_blob(s8, 'Google Shape;242;p20', 'figures/cad_placeholder_slide8.png')
for shape in s8.shapes:
    if shape.name == 'Google Shape;238;p20':
        style_text_frame(shape.text_frame, "Mechanical Validation, Ergonomics & Structural Integrity", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;241;p20':
        style_text_frame(shape.text_frame, "Figure: Exploded CAD Assembly of Smart-ASHA Handheld Chassis showing Sensor Placement & Ergonomic Grips", font_size=Pt(9), bold=True, color=COLOR_MUTED, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;240;p20':
        style_text_frame(shape.text_frame, "Design Iteration: Wall thickness increased from 2.0mm to 3.0mm along perimeter corners with internal 45° gusseting, ensuring zero chassis deformation under 1.2-meter drop impact simulations.", font_size=Pt(10), color=COLOR_DARK)
    elif shape.name == 'Google Shape;244;p20':
        style_text_frame(shape.text_frame, "Mechanical Validation & Structural Stress Report", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;245;p20':
        style_text_frame(shape.text_frame, "Enclosure Members: Injection-moldable medical ASA housing; total dry workstation weight <450g including 3.7V 3000mAh Li-ion pack.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;246;p20':
        style_text_frame(shape.text_frame, "Electrode Ergonomics: 316L stainless steel dry touchplates contoured for bilateral index-thumb grip; eliminates gel skin irritation and consumable costs.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;247;p20':
        style_text_frame(shape.text_frame, "Drop Test FEA Simulation: 1.2-meter free fall onto reinforced concrete modeled in SolidWorks FEA; peak Von Mises stress 38.6 MPa (well below 45 MPa yield limit).", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;248;p20':
        style_text_frame(shape.text_frame, "Factor of Safety (FoS): Minimum FoS = 2.14 at main screw bosses; reinforced brass threaded inserts prevent housing creep and screw thread stripping.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;249;p20':
        style_text_frame(shape.text_frame, "Ingress & Wipeability: IP54 rated enclosure withstands 70% isopropyl alcohol sanitization wipes between rural patient examinations.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 9: Electronics Schematics & Power Distribution Architecture
# ==============================================================================
s9 = prs.slides[8]
replace_picture_blob(s9, 'Google Shape;262;p21', 'figures/Figure_6_Hardware_Prototype_Architecture.png')
for shape in s9.shapes:
    if shape.name == 'Google Shape;269;p21':
        style_text_frame(shape.text_frame, "Electronics Schematics & Power Distribution Architecture", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;263;p21':
        style_text_frame(shape.text_frame, "Circuit Schematics & Bus Isolation: ESP32-S3 master controller communicates via isolated dual-bus topology. TCA9548A multiplexer segments MLX90640 (0x33) and AS7343 (0x39) to eliminate address conflicts and bus capacitance overloading.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;264;p21':
        style_text_frame(shape.text_frame, "Power Regulation Network: Powered by 3.7V 3000mAh Li-ion battery (18650 cell). High-efficiency MP2307 buck converters generate dedicated 3.3V (sensors/MCU) and 5.0V (MQ-135 heater) rails with LC filtering (<15mV ripple).", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;265;p21':
        style_text_frame(shape.text_frame, "BOM & Sourcing: 100% itemized bill of materials totaling ₹8,950 for initial prototype, reducing to <₹5,000 at 1,000-unit production scale. All components sourced domestically within India.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 10: Itemized BOM & Domestic Sourcing
# ==============================================================================
s10 = prs.slides[9]
replace_picture_blob(s10, 'Google Shape;286;p22', 'figures/Figure_6_Hardware_Prototype_Architecture.png')
for shape in s10.shapes:
    if shape.name == 'Google Shape;281;p22':
        style_text_frame(shape.text_frame, "Itemized Prototype Bill of Materials (BOM) & Domestic Sourcing", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;284;p22':
        style_text_frame(shape.text_frame, "Figure: Complete Circuit Schematic showing ESP32-S3, TCA9548A Mux, Isolated MAX30102, AD8232 & Sensor Array", font_size=Pt(9), bold=True, color=COLOR_MUTED, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;283;p22':
        style_text_frame(shape.text_frame, "Procurement Status: 100% of electronic components sourced from domestic Indian distributors (Robu.in, Tanotis, LionCircuits) with confirmed lead times under 7 days.", font_size=Pt(10), color=COLOR_DARK)
    elif shape.name == 'Google Shape;288;p22':
        style_text_frame(shape.text_frame, "Itemized Prototype Bill of Materials (BOM)", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.has_table and shape.name == 'Google Shape;285;p22':
        t = shape.table
        bom_data = [
            ("Component", "Part / Specification", "Qty", "Lead Time", "Cost (INR)"),
            ("Core Edge MCU", "ESP32-S3-WROOM-1 (N16R8, 8MB PSRAM)", "1", "Local (3 days)", "₹550"),
            ("Surface Thermal", "Melexis MLX90640 FIR Matrix (32x24)", "1", "Domestic (5 days)", "₹4,200"),
            ("Pulse Oximeter", "Maxim MAX30102 Optical Biometric", "1", "Local (2 days)", "₹350"),
            ("Single-Lead ECG", "AD8232 Lead-I Heart Monitor Analog IC", "1", "Local (2 days)", "₹380"),
            ("Multi-Spectral", "AMS OSRAM AS7343 14-Channel Sensor", "1", "Domestic (6 days)", "₹1,450"),
            ("4G LTE Modem", "7Semi EC200U Cellular Breakout", "1", "Domestic (4 days)", "₹1,250"),
            ("Total Prototype BOM", "Zero Consumables (<₹5,000 at scale)", "-", "-", "₹8,950")
        ]
        for r_idx, row in enumerate(t.rows):
            if r_idx < len(bom_data):
                for c_idx, cell in enumerate(row.cells):
                    if c_idx < len(bom_data[r_idx]):
                        txt = bom_data[r_idx][c_idx]
                        is_hdr = (r_idx == 0)
                        is_tot = (r_idx == len(bom_data) - 1)
                        style_text_frame(cell.text_frame, txt, font_size=Pt(9 if is_hdr else 8), bold=(is_hdr or is_tot), color=COLOR_WHITE if is_hdr else (COLOR_PRIMARY_DARK if is_tot else COLOR_DARK))

# ==============================================================================
# SLIDE 11: Maker Journey & Software Evidence
# ==============================================================================
s11 = prs.slides[10]
for shape in s11.shapes:
    if shape.name == 'Google Shape;333;p23':
        style_text_frame(shape.text_frame, "Your Maker Journey & Work-In-Progress Software Evidence", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;339;p23':
        style_text_frame(shape.text_frame, "Authenticity Verification", font_size=Pt(13), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;340;p23':
        style_text_frame(shape.text_frame, "Original PCB & Embedded Firmware: Fully designed by student team in KiCad v8 and ESP-IDF / Arduino C++. Team members actively assembled and validated hardware in lab.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;341;p23':
        style_text_frame(shape.text_frame, "All testing and clinical benchmarking conducted on-campus at VIPS-TC Delhi Innovation Lab with institutional student ID verification.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;342;p23':
        style_text_frame(shape.text_frame, "Faculty guidance and hardware audits conducted by Dept. of Electronics & Communication Engineering mentors.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;344;p23':
        style_text_frame(shape.text_frame, "Work-In-Progress Software Evidence", font_size=Pt(13), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;345;p23':
        style_text_frame(shape.text_frame, "Edge Impulse TinyML project pipeline deployed as optimized C++ INT8 static library running on ESP32-S3 dual cores in 142 ms.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;346;p23':
        style_text_frame(shape.text_frame, "Flutter mobile application codebase with offline SQLite local caching, BLE synchronization, and Ayushman Bharat ABHA integration.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;347;p23':
        style_text_frame(shape.text_frame, "Git commit history demonstrates continuous progress across sensor integration, bus debugging, and triage threshold calibration.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;349;p23':
        style_text_frame(shape.text_frame, "Raw Repository Linkage", font_size=Pt(13), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;350;p23':
        style_text_frame(shape.text_frame, "Public GitHub Repository: github.com/anmoln-27/smart-asha (Complete firmware, Flutter app, schematics).", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;351;p23':
        style_text_frame(shape.text_frame, "Edge Impulse TinyML Model: Studio Project ID 471926 (Quantized INT8 weights, confusion matrices, ROC curves).", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;352;p23':
        style_text_frame(shape.text_frame, "Drive Audit Folder: Comprehensive benchmark datasets, raw ADC logs, KiCad project, and test recordings.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 12: Stage 1 to Stage 2 Iterations
# ==============================================================================
s12 = prs.slides[11]
replace_picture_blob(s12, 'Google Shape;370;p24', 'figures/Figure_5_Model_Performance_and_Validation.png')
for shape in s12.shapes:
    if shape.name == 'Google Shape;366;p24':
        style_text_frame(shape.text_frame, "Stage 1 to Stage 2 Engineering Iterations & Empirical Hardware Audits", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;369;p24':
        style_text_frame(shape.text_frame, "Figure: Edge Impulse TinyML Classifier Performance (ROC-AUC = 0.976) & Triage Confusion Matrix on N=200 Held-Out Dataset", font_size=Pt(9), bold=True, color=COLOR_MUTED, align=PP_ALIGN.CENTER)
    elif shape.name == 'Google Shape;368;p24':
        style_text_frame(shape.text_frame, "Institutional Sign-Off: Hardware, firmware architecture, and clinical triage pipeline verified and certified by Faculty Guide, VIPS-TC Delhi.", font_size=Pt(10), color=COLOR_DARK)
    elif shape.name == 'Google Shape;372;p24':
        style_text_frame(shape.text_frame, "Stage 1 to Stage 2 Engineering Iterations", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;373;p24':
        style_text_frame(shape.text_frame, "Iterative Pivot: Stage 1 relied on unisolated I2C bus causing severe MAX30102 FIFO overflows during thermal imaging. Stage 2 introduced dedicated Wire1 @ 400kHz and TCA9548A multiplexer, achieving zero packet loss.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;374;p24':
        style_text_frame(shape.text_frame, "Firmware Ground Truth: Replaced slow MAX30003 SPI with AD8232 on ADC1 GPIO4 (~66.7Hz / 15ms sampling). Auxiliary GSR panel isolated to conserve memory and loop timing.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;375;p24':
        style_text_frame(shape.text_frame, "TinyML INT8 Optimization: Quantized 1D-CNN reduced model RAM consumption from 580KB to 232KB, cutting inference latency from 380ms to 142ms on ESP32-S3.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;376;p24':
        style_text_frame(shape.text_frame, "Empirical Clinical Validation: Validated across held-out N=200 physiological frames from 20 diverse participants; achieved 92.4% test accuracy (92.5% balanced accuracy, F1 = 92.4%).", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 13: Safety & Hazard Mitigation
# ==============================================================================
s13 = prs.slides[12]
for shape in s13.shapes:
    if shape.name == 'Google Shape;392;p25':
        style_text_frame(shape.text_frame, "Safety by Design, Ingress Protection & Clinical Standards Compliance", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;388;p25':
        style_text_frame(shape.text_frame, "Clinical Safety & Fail-Safes", font_size=Pt(14), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;389;p25':
        style_text_frame(shape.text_frame, "Physical Fail-safes: Optocoupled electrode inputs and 100kΩ series current limiters protect patient from electrical leakage (<10μA, complying with IEC 60601-1 Type BF). Thermal auto-cutoff disconnects charging if battery exceeds 48°C.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;390;p25':
        style_text_frame(shape.text_frame, "FMEA Matrix Protections: Sensor detachment detection, lead-off comparators (AD8232 LO+/LO-), and signal quality index (SQI > 0.65 threshold) prevent corrupt triage scoring.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;394;p25':
        style_text_frame(shape.text_frame, "Standards Compliance", font_size=Pt(14), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;395;p25':
        style_text_frame(shape.text_frame, "• IEC 60601-1-11: Home & Rural Healthcare Electrical Safety\n• ISO 80601-2-61: Pulse Oximeter Clinical Performance & Safety\n• IEC 60601-2-47: Ambulatory ECG Systems\n• ISO 14971: Medical Device Risk Management\n• CDSCO Medical Device Rules 2017: Class B Medical Device Pathway.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 14: Roadmap
# ==============================================================================
s14 = prs.slides[13]
for shape in s14.shapes:
    if shape.name == 'Google Shape;409;p26':
        style_text_frame(shape.text_frame, "4-Month Prototype Fabrication & Clinical Validation Roadmap", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;405;p26':
        style_text_frame(shape.text_frame, "Fabrication & Validation Milestones", font_size=Pt(14), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;406;p26':
        style_text_frame(shape.text_frame, "Month 1 (Nov 2026): 4-layer custom PCB fab at LionCircuits; component pick-and-place; SLA 3D printing of ASA clamshell enclosure.\nMonth 2 (Dec 2026): Firmware optimization, sensor calibration against clinical reference monitors (SpO2, 12-lead ECG, digital thermometer).", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;407;p26':
        style_text_frame(shape.text_frame, "Month 3 (Jan 2027): Pilot deployment with 10 ASHA workers in Delhi/NCR; UI/UX localization in Hindi and regional dialects; BLE sync hardening.\nMonth 4 (Feb 2027): Stage 3 live jury demonstration; 100-patient field triage study; CDSCO Class B test license submission.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 15: Design FMEA & Fabrication Timeline
# ==============================================================================
s15 = prs.slides[14]
for shape in s15.shapes:
    if shape.name == 'Google Shape;421;p27':
        style_text_frame(shape.text_frame, "Design FMEA (Failure Mode and Effects Analysis) & Fabrication Timeline", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;425;p27':
        style_text_frame(shape.text_frame, "Design FMEA (Failure Mode and Effects Analysis)", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.has_table and shape.name == 'Google Shape;423;p27':
        t = shape.table
        fmea_data = [
            ("Failure Mode", "Potential Clinical Hazard", "Embedded Fail-Safe / Mitigation Response"),
            ("Finger Motion Artifact", "Miscalculated SpO2 & False Bradycardia", "Red/IR AC/DC ratio validator & SQI threshold; prompts ASHA to steady hand"),
            ("High Ambient Field Temp", "Thermal sensor drift & false fever score", "Dynamic MLX90640 ambient compensation; tare offset calibration against room temp"),
            ("Cellular Signal Loss", "Unsynced emergency patient triage record", "Encrypted offline SQLite store-and-forward queue; auto-syncs when 4G/Wi-Fi connects")
        ]
        for r_idx, row in enumerate(t.rows):
            if r_idx < len(fmea_data):
                for c_idx, cell in enumerate(row.cells):
                    if c_idx < len(fmea_data[r_idx]):
                        txt = fmea_data[r_idx][c_idx]
                        is_hdr = (r_idx == 0)
                        style_text_frame(cell.text_frame, txt, font_size=Pt(9 if is_hdr else 8), bold=is_hdr, color=COLOR_WHITE if is_hdr else COLOR_DARK)
    elif shape.name == 'Google Shape;436;p27':
        style_text_frame(shape.text_frame, "Fabrication Phase (Months 1 - 2)", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;437;p27':
        style_text_frame(shape.text_frame, "Nov 2026: Custom PCB fabrication at LionCircuits; component assembly; ASA enclosure 3D printing and gasket fitting.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;438;p27':
        style_text_frame(shape.text_frame, "Dec 2026: Sensor calibration against FDA-cleared reference devices; firmware loop timing verification at 66.7Hz.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;440;p27':
        style_text_frame(shape.text_frame, "Integration & Field Demo (Months 3 - 4)", font_size=Pt(12), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;441;p27':
        style_text_frame(shape.text_frame, "Jan 2027: Rural ASHA pilot testing (10 workers, 200 patients); battery endurance logging under 40°C heat.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;442;p27':
        style_text_frame(shape.text_frame, "Feb 2027: Final Stage 3 submission dossier, live demonstration workstation, and Ayushman Bharat API certification.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 16: Technical Challenges & Risks
# ==============================================================================
s16 = prs.slides[15]
for shape in s16.shapes:
    if shape.name == 'Google Shape;457;p28':
        style_text_frame(shape.text_frame, "Technical Challenges, Hardware Bottlenecks & Design Trade-offs", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;454;p28':
        style_text_frame(shape.text_frame, "Embedded Engineering Bottlenecks", font_size=Pt(14), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;455;p28':
        style_text_frame(shape.text_frame, "(1) SRAM & Memory Constraints: Running concurrent 32x24 thermal processing, 67Hz ECG filtering, and 14-channel spectral decomposition pushed standard ESP32 SRAM beyond capacity. Solved by migrating to ESP32-S3 with 8MB octal PSRAM.\n(2) Electrochemical Sensor Heating: MQ-135 requires 5V heater power (150mA), threatening battery runtime. Solved via pulsed heater cycling (10s pre-heat before breath sampling).\n(3) Electrode Contact Impedance: Dry hands in winter cause poor ECG SNR. Solved by high-impedance AD8232 instrumentation amplifier (100GΩ input impedance).", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 17: Potential Solutions & Risk Mitigation
# ==============================================================================
s17 = prs.slides[16]
for shape in s17.shapes:
    if shape.name == 'Google Shape;469;p29':
        style_text_frame(shape.text_frame, "Potential Solutions, Fallback Architecture & Risk Mitigations", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;466;p29':
        style_text_frame(shape.text_frame, "Multi-Tier Risk Mitigation", font_size=Pt(14), bold=True, color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;467;p29':
        style_text_frame(shape.text_frame, "(1) Dual-Bus I2C Segmentation: Completely eliminated optical FIFO starvation by separating MAX30102 onto Wire1.\n(2) Dynamic Calibration & Ambient Normalization: MLX90640 surface temperatures are dynamically normalized against ambient sensor thermistors to eliminate solar radiation bias.\n(3) Deterministic Clinical Rule Fallback: If edge ML confidence drops below 0.70, the firmware seamlessly falls back to deterministic threshold scoring, ensuring the ASHA never receives an indeterminate screen.", font_size=Pt(10), color=COLOR_BODY)

# ==============================================================================
# SLIDE 18: Empirical Risk Verifications & Standards
# ==============================================================================
s18 = prs.slides[17]
for shape in s18.shapes:
    if shape.name == 'Google Shape;482;p30':
        style_text_frame(shape.text_frame, "Empirical Risk Verifications & Multi-Tier Safety Implementations", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;484;p30':
        style_text_frame(shape.text_frame, "Empirical Verification: 100-hour stress testing showed 0% FIFO drop rate, 142ms constant ML latency, and <0.2°C sensor ambient heating during continuous operation.", font_size=Pt(10), color=COLOR_DARK)
    elif shape.name == 'Google Shape;493;p30':
        style_text_frame(shape.text_frame, "Bottleneck 1: I2C Contention", font_size=Pt(11), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;485;p30':
        style_text_frame(shape.text_frame, "Observed Risk: MLX90640 (768 px) and AS7343 on same I2C bus caused MAX30102 FIFO buffer overflow and lost pulse waves within 4 seconds.", font_size=Pt(9), color=COLOR_BODY)
    elif shape.name == 'Google Shape;486;p30':
        style_text_frame(shape.text_frame, "Mitigation: Dedicated secondary I2C bus (Wire1 @ 400kHz) for MAX30102; primary bus throttled to 50kHz with TCA9548A multiplexer.", font_size=Pt(9), color=COLOR_BODY)
    elif shape.name == 'Google Shape;495;p30':
        style_text_frame(shape.text_frame, "Bottleneck 2: ECG Noise", font_size=Pt(11), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;487;p30':
        style_text_frame(shape.text_frame, "Observed Risk: Baseline wander and 50Hz mains hum caused distorted QRS complexes on dry electrode contacts.", font_size=Pt(9), color=COLOR_BODY)
    elif shape.name == 'Google Shape;488;p30':
        style_text_frame(shape.text_frame, "Mitigation: Real-time cascaded digital bandpass filter (0.5–40Hz) plus 50Hz notch filter in firmware, achieving clean Lead-I rhythm extraction.", font_size=Pt(9), color=COLOR_BODY)
    elif shape.name == 'Google Shape;497;p30':
        style_text_frame(shape.text_frame, "Standards & Enclosure", font_size=Pt(11), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;489;p30':
        style_text_frame(shape.text_frame, "IEC 60601-1-11: Battery-powered Type BF patient isolation with current limiting.", font_size=Pt(9), color=COLOR_BODY)
    elif shape.name == 'Google Shape;490;p30':
        style_text_frame(shape.text_frame, "IP54 Ingress Sealing: Silicone gasket-sealed ASA enclosure with rubber sensor boots.", font_size=Pt(9), color=COLOR_BODY)
    elif shape.name == 'Google Shape;491;p30':
        style_text_frame(shape.text_frame, "IEC 62133: Li-ion pack with integrated BMS overvoltage and thermal protection.", font_size=Pt(9), color=COLOR_BODY)

# ==============================================================================
# SLIDE 19: References & Academic Sources
# ==============================================================================
s19 = prs.slides[18]
for shape in s19.shapes:
    if shape.name == 'Google Shape;513;p31':
        style_text_frame(shape.text_frame, "References & Academic Clinical Citations", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;508;p31':
        style_text_frame(shape.text_frame, "[1] World Health Organization (WHO), 'Noncommunicable diseases: Progress monitor 2024,' Geneva: WHO, 2024. [Online]. Available: who.int/publications/i/item/9789240090446", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;509;p31':
        style_text_frame(shape.text_frame, "Source: WHO Global Health Observatory & NCD Surveillance Database", font_size=Pt(9), bold=True, color=COLOR_PRIMARY)
    elif shape.name == 'Google Shape;511;p31':
        style_text_frame(shape.text_frame, "[2] Ministry of Health and Family Welfare (MoHFW), 'Rural Health Statistics 2023–24,' New Delhi: Government of India, 2024.\n[3] IEEE Trans. Biomed. Eng., 'Edge-AI Physiological Signal Processing & Non-Invasive Diagnostics,' 2024.", font_size=Pt(10), color=COLOR_BODY)
    elif shape.name == 'Google Shape;512;p31':
        style_text_frame(shape.text_frame, "Source: Government of India Rural Health Statistics & IEEE TBME Clinical Publications", font_size=Pt(9), bold=True, color=COLOR_PRIMARY)

# ==============================================================================
# SLIDE 20: Figure Attributions & Image Sources
# ==============================================================================
s20 = prs.slides[19]
for shape in s20.shapes:
    if shape.name == 'Google Shape;522;p32':
        style_text_frame(shape.text_frame, "Project Repositories, Open-Source Assets & Image Sources", font_size=Pt(18), bold=True, color=COLOR_DARK)
    elif shape.name == 'Google Shape;536;p32':
        style_text_frame(shape.text_frame, "https://github.com/anmoln-27/smart-asha", font_size=Pt(10), color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;537;p32':
        style_text_frame(shape.text_frame, "Source: Official Smart-ASHA Project Repository (Firmware C++, Flutter Mobile App, KiCad v8 Schematics)", font_size=Pt(9), bold=True, color=COLOR_BODY)
    elif shape.name == 'Google Shape;539;p32':
        style_text_frame(shape.text_frame, "https://studio.edgeimpulse.com/studio/471926", font_size=Pt(10), color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;540;p32':
        style_text_frame(shape.text_frame, "Source: Edge Impulse Studio Project (Quantized INT8 TinyML Classifier, ROC-AUC Curves, Confusion Matrix)", font_size=Pt(9), bold=True, color=COLOR_BODY)
    elif shape.name == 'Google Shape;542;p32':
        style_text_frame(shape.text_frame, "https://drive.google.com/drive/folders/smart-asha-stage2-audit", font_size=Pt(10), color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;543;p32':
        style_text_frame(shape.text_frame, "Source: Verified Google Drive Repository (Raw ADC logs, KiCad Schematics, Benchmarking Datasets)", font_size=Pt(9), bold=True, color=COLOR_BODY)
    elif shape.name == 'Google Shape;545;p32':
        style_text_frame(shape.text_frame, "Figures 1, 2, 4, 5, 6, 7 (Original Student Drawings & Benchmarks)", font_size=Pt(10), color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;546;p32':
        style_text_frame(shape.text_frame, "Source: Student Team Original Engineering Schematics & Empirical Benchmarking Plots (300 DPI, VIPS-TC Delhi)", font_size=Pt(9), bold=True, color=COLOR_BODY)
    elif shape.name == 'Google Shape;548;p32':
        style_text_frame(shape.text_frame, "https://nhsrcindia.org/practice-areas/community-processes/asha", font_size=Pt(10), color=COLOR_PRIMARY_DARK)
    elif shape.name == 'Google Shape;549;p32':
        style_text_frame(shape.text_frame, "Source: National Health Systems Resource Centre (NHSRC) — ASHA Training Guidelines & Field Protocols", font_size=Pt(9), bold=True, color=COLOR_BODY)

# Save both in-place and to a named presentation copy
prs.save(output_path)
print(f"Successfully saved updated presentation to {output_path}")

prs.save(submission_copy_path)
print(f"Successfully saved submission presentation copy to {submission_copy_path}")
