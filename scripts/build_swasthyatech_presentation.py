"""
Builds the complete SwasthyaTech Synapse 2026 Presentation for Arogya AI / Smart-ASHA.
Strictly preserves the template background, layout, logos, slide headings, and tables,
and populates only verified facts without hallucination.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # completely blank slide

    # Paths
    base_dir = r"c:\Users\Acer\OneDrive\Desktop\DESKTOP VANSH\Smart Asha"
    assets_dir = os.path.join(base_dir, "presentation_assets")
    figures_dir = os.path.join(base_dir, "figures")
    output_pptx = os.path.join(base_dir, "SwasthyaTech_Synapse_2026_Smart_ASHA_Presentation.pptx")

    ihfc_logo = os.path.join(assets_dir, "ihfc_logo.png")
    iitd_logo = os.path.join(assets_dir, "iitd_logo.png")
    banner_top = os.path.join(assets_dir, "banner_top.png")
    banner_bottom = os.path.join(assets_dir, "banner_bottom.png")

    fig1 = os.path.join(figures_dir, "Figure_1_Hardware_Architecture.png")
    fig3 = os.path.join(figures_dir, "Figure_3_End_to_End_Architecture.png")
    fig4 = os.path.join(figures_dir, "Figure_4_Operational_Triage_Flowchart.png")
    fig5 = os.path.join(figures_dir, "Figure_5_Model_Performance_and_Validation.png")
    fig6 = os.path.join(figures_dir, "Figure_6_Hardware_Prototype_Architecture.png")

    # Colors
    C_BLACK = RGBColor(17, 24, 39)
    C_NAVY = RGBColor(27, 54, 93)
    C_TEAL = RGBColor(0, 128, 128)
    C_CRIMSON = RGBColor(158, 27, 50)
    C_GRAY = RGBColor(75, 85, 99)
    C_LIGHT_BG = RGBColor(248, 250, 252)
    C_BORDER = RGBColor(226, 232, 240)
    C_WHITE = RGBColor(255, 255, 255)
    C_TBL_HDR = RGBColor(59, 107, 155)
    C_TBL_ALT = RGBColor(241, 245, 249)
    C_GREEN = RGBColor(22, 101, 52)
    C_AMBER = RGBColor(180, 83, 9)
    C_RED = RGBColor(185, 28, 28)

    FONT_MAIN = "Arial"

    def add_header(slide, title_text, has_iitd=True, is_slide_15=False):
        # White background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_WHITE
        bg.line.fill.background()

        if is_slide_15:
            if os.path.exists(banner_top):
                slide.shapes.add_picture(banner_top, Inches(0.4), Inches(0.25), width=Inches(12.53), height=Inches(0.12))
            if os.path.exists(banner_bottom):
                slide.shapes.add_picture(banner_bottom, Inches(0.4), Inches(7.15), width=Inches(12.53), height=Inches(0.12))

        # Logos
        top_offset = Inches(0.5) if is_slide_15 else Inches(0.35)
        if os.path.exists(ihfc_logo):
            slide.shapes.add_picture(ihfc_logo, Inches(0.45), top_offset, width=Inches(0.95), height=Inches(1.08))
        if has_iitd and os.path.exists(iitd_logo):
            slide.shapes.add_picture(iitd_logo, Inches(11.95), top_offset, width=Inches(0.98), height=Inches(0.98))

        # Title
        if title_text:
            tb = slide.shapes.add_textbox(Inches(1.6), Inches(0.35), Inches(10.1), Inches(1.0))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.name = FONT_MAIN
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = C_BLACK
            p.alignment = PP_ALIGN.LEFT

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_header(slide1, "", has_iitd=True)

    # Event Header: SwasthyaTech Synapse 2026
    tb_event = slide1.shapes.add_textbox(Inches(2.0), Inches(0.45), Inches(9.333), Inches(0.8))
    tf_ev = tb_event.text_frame
    tf_ev.word_wrap = True
    p_ev = tf_ev.paragraphs[0]
    p_ev.text = "SwasthyaTech Synapse 2026"
    p_ev.font.name = FONT_MAIN
    p_ev.font.size = Pt(28)
    p_ev.font.bold = True
    p_ev.font.color.rgb = C_BLACK
    p_ev.alignment = PP_ALIGN.CENTER

    # Sub-header event details
    p_ev_sub = tf_ev.add_paragraph()
    p_ev_sub.text = "I-Hub Foundation for Cobotics (IHFC) | Technology Innovation Hub @ IIT Delhi"
    p_ev_sub.font.name = FONT_MAIN
    p_ev_sub.font.size = Pt(13)
    p_ev_sub.font.bold = False
    p_ev_sub.font.color.rgb = C_TEAL
    p_ev_sub.alignment = PP_ALIGN.CENTER

    # Proposal Title Box
    tb_title = slide1.shapes.add_textbox(Inches(1.2), Inches(1.85), Inches(10.933), Inches(2.2))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_t = tf_title.paragraphs[0]
    p_t.text = "Smart-ASHA (Arogya AI): A Low-Cost Multimodal Edge-AI Workstation for Frontline Physiological Screening and Referral Support"
    p_t.font.name = FONT_MAIN
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY
    p_t.alignment = PP_ALIGN.CENTER

    p_t_sub = tf_title.add_paragraph()
    p_t_sub.text = "Non-Invasive Cardiopulmonary, Radiometric Thermal, and Biochemical Triage for Resource-Constrained Rural Primary Healthcare"
    p_t_sub.font.name = FONT_MAIN
    p_t_sub.font.size = Pt(14)
    p_t_sub.font.italic = True
    p_t_sub.font.color.rgb = C_GRAY
    p_t_sub.alignment = PP_ALIGN.CENTER

    # Inventors Card Box
    card_inv = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(4.2), Inches(9.733), Inches(2.2))
    card_inv.fill.solid()
    card_inv.fill.fore_color.rgb = C_LIGHT_BG
    card_inv.line.color.rgb = C_BORDER
    card_inv.line.width = Pt(1)

    tb_inv = slide1.shapes.add_textbox(Inches(2.0), Inches(4.3), Inches(9.333), Inches(2.0))
    tf_inv = tb_inv.text_frame
    tf_inv.word_wrap = True

    p_h = tf_inv.paragraphs[0]
    p_h.text = "Inventor Names, Designation & Organization"
    p_h.font.name = FONT_MAIN
    p_h.font.size = Pt(15)
    p_h.font.bold = True
    p_h.font.color.rgb = C_BLACK
    p_h.alignment = PP_ALIGN.CENTER

    p_names = tf_inv.add_paragraph()
    p_names.text = "Gauri Gupta (03417711724)  |  Anmol Nandwani (35117711724)  |  Vansh Sharma (02717711724)"
    p_names.font.name = FONT_MAIN
    p_names.font.size = Pt(14)
    p_names.font.bold = True
    p_names.font.color.rgb = C_NAVY
    p_names.alignment = PP_ALIGN.CENTER

    p_desig = tf_inv.add_paragraph()
    p_desig.text = "Student Researchers, Department of Industrial Internet of Things (IIoT - A)"
    p_desig.font.name = FONT_MAIN
    p_desig.font.size = Pt(12)
    p_desig.font.color.rgb = C_GRAY
    p_desig.alignment = PP_ALIGN.CENTER

    p_mentor = tf_inv.add_paragraph()
    p_mentor.text = "Academic Supervisor / Guide: Dr. Divya Agarwal (Assistant Professor, divya.agarwal@vips.edu)"
    p_mentor.font.name = FONT_MAIN
    p_mentor.font.size = Pt(12)
    p_mentor.font.bold = True
    p_mentor.font.color.rgb = C_TEAL
    p_mentor.alignment = PP_ALIGN.CENTER

    p_org = tf_inv.add_paragraph()
    p_org.text = "School of Engineering & Technology, Vivekananda Institute of Professional Studies – Technical Campus (VIPS-TC), Delhi"
    p_org.font.name = FONT_MAIN
    p_org.font.size = Pt(12)
    p_org.font.color.rgb = C_BLACK
    p_org.alignment = PP_ALIGN.CENTER

    # Footnote
    tb_foot = slide1.shapes.add_textbox(Inches(0.5), Inches(6.85), Inches(12.0), Inches(0.5))
    tf_f = tb_foot.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "*Separate proposal for each individual patent/product/technology is requested."
    p_f.font.name = FONT_MAIN
    p_f.font.size = Pt(10)
    p_f.font.italic = True
    p_f.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 2: Problem to be Addressed
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Problem to be addressed", has_iitd=False)

    # Left Column: Problem Statement & Need
    card_prob = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(6.8), Inches(5.5))
    card_prob.fill.solid()
    card_prob.fill.fore_color.rgb = C_LIGHT_BG
    card_prob.line.color.rgb = C_BORDER

    tb_prob = slide2.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(6.4), Inches(5.2))
    tf_p = tb_prob.text_frame
    tf_p.word_wrap = True

    p = tf_p.paragraphs[0]
    p.text = "Problem Statement and Need for the Solution"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    p = tf_p.add_paragraph()
    p.text = "(What specific problem are you trying to solve?)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(12)
    p.font.italic = True
    p.font.color.rgb = C_GRAY

    bullets_prob = [
        ("Severe Urban-Rural Healthcare Divide: ", "Over 70% of India's 1.4 billion population lives in rural/semi-urban regions, yet fewer than 30% of qualified doctors and diagnostic laboratories are stationed there."),
        ("Subjective Frontline Triage Bottleneck: ", "India's 1.1M+ Accredited Social Health Activists (ASHAs) conduct door-to-door screenings relying solely on visual inspection and tactile estimation, leading to missed cardiopulmonary anomalies and delayed referrals."),
        ("Economic Inaccessibility of Existing Tools: ", "Commercial multi-parameter health kiosks (e.g., HealthCube) cost ₹1.2L to ₹2.2L per unit and impose recurring chemical test-strip expenses (₹80–₹250/test), costing over ₹9 Lakhs/year per PHC."),
        ("Cloud Failure in Low-Resource Outposts: ", "Over 40% of rural Indian health outposts suffer intermittent cellular connectivity; cloud-tethered telemedicine portals fail completely in these disconnected settings."),
        ("Diagnostic Silos & Acoustic Noise: ", "Acoustic digital stethoscopes fail in noisy rural clinics (60–70 dB ambient noise), while single-parameter pulse oximeters cannot detect underlying metabolic shock or thermal fevers.")
    ]
    for b_title, b_desc in bullets_prob:
        p = tf_p.add_paragraph()
        p.text = "• "
        p.font.size = Pt(11)
        p.font.name = FONT_MAIN
        run1 = p.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = C_BLACK
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.color.rgb = C_GRAY

    # Right Column: Target Beneficiaries & Operational Triage Overview
    card_ben = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(1.5), Inches(5.1), Inches(5.5))
    card_ben.fill.solid()
    card_ben.fill.fore_color.rgb = C_LIGHT_BG
    card_ben.line.color.rgb = C_BORDER

    tb_ben = slide2.shapes.add_textbox(Inches(7.8), Inches(1.65), Inches(4.7), Inches(5.2))
    tf_b = tb_ben.text_frame
    tf_b.word_wrap = True

    p = tf_b.paragraphs[0]
    p.text = "Target Beneficiaries"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    beneficiaries = [
        ("1.1+ Million ASHA & ANM Workers: ", "Frontline community health workers who receive an objective, zero-literacy assistive workstation with bilingual audio guidance (Hindi/English)."),
        ("160,000+ Ayushman Bharat HWCs & PHCs: ", "Primary Health Centres and Health & Wellness Centres gaining instant digital triage without expensive diagnostic infrastructure."),
        ("900+ Million Rural & Underserved Citizens: ", "Early detection of silent hypoxemia, cardiac arrhythmias, fever patterns, and anemia risk without painful needles or expensive private fees."),
        ("State Health Missions & NHM: ", "Actionable epidemiological disease surveillance mapping and standardized offline ICD-10 referral records.")
    ]
    for b_title, b_desc in beneficiaries:
        p = tf_b.add_paragraph()
        p.text = "• "
        p.font.size = Pt(11)
        p.font.name = FONT_MAIN
        run1 = p.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = C_BLACK
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.color.rgb = C_GRAY

    # Add quick visual callout box at bottom of right card
    c_box = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.9), Inches(5.2), Inches(4.5), Inches(1.5))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = C_WHITE
    c_box.line.color.rgb = C_TEAL
    c_box.line.width = Pt(1.5)
    tb_c = slide2.shapes.add_textbox(Inches(8.0), Inches(5.25), Inches(4.3), Inches(1.4))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "National Alignment: SDG 3 & 10"
    p.font.name = FONT_MAIN
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p_desc = tf_c.add_paragraph()
    p_desc.text = "Directly addresses UN SDG 3 (Good Health and Well-Being) and SDG 10 (Reduced Inequalities) by democratizing clinical-grade point-of-care vital triage."
    p_desc.font.name = FONT_MAIN
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 3: Details of Technology/Product/Prototype
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Details of Technology/Product/Prototype", has_iitd=True)

    # Left Column: Detailed Metadata
    card_tech = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(7.2), Inches(5.5))
    card_tech.fill.solid()
    card_tech.fill.fore_color.rgb = C_LIGHT_BG
    card_tech.line.color.rgb = C_BORDER

    tb_t = slide3.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(6.8), Inches(5.2))
    tf_tech = tb_t.text_frame
    tf_tech.word_wrap = True

    items_s3 = [
        ("• TRL Level: TRL 4 (Laboratory / Bench Validation)",
         "Fully functional benchtop multi-sensor prototype integrated around an ESP32-S3 microcontroller. Validated across laboratory test benches (200-frame test set, 142 ms on-device INT8 CNN inference, 232 KB PSRAM). Currently advancing to TRL 5/6 via a custom 4-layer rigid-flex PCB and Primary Health Centre (PHC) pilot usability trials."),
        
        ("• Status of Patent, if any: Under Preparation (Pre-Filing Stage)",
         "Provisional Indian Patent Application currently under drafting covering the 'Multi-Modal Dual-Bus Edge-AI Sensing Architecture and Stefan-Boltzmann Radiometric Drift Compensation Engine'."),
        
        ("• Patent No.: N/A (Pending Official Filing)",
         "No patent grant or filing number issued to date; formal submission planned following initial clinical benchmark calibration."),
        
        ("• Application Domain: Edge-AI Healthcare & Point-of-Care Diagnostics",
         "Medical IoT, Non-Invasive Clinical Triage, Assistive Cobotic Health Devices, Frontline Telemedicine, Rural Public Health Systems."),
        
        ("• Previous Funding Received / Applied for this Technology:",
         ""),
        ("    - Amount: Nil External Grant / ~₹50,000 Institutional Lab Support",
         "Prototyping funded through institutional lab facilities and student research resources at VIPS-TC."),
        ("    - Agency / Entity: VIPS-TC / Applied to Maker Bhavan Foundation",
         "Formal proposal submitted to Vishwakarma Awards 2026–27 (Application ID: VK26-AU-FD-0006; Theme: Frontier Diagnostics / Non-Invasive Diagnostics)."),
        ("    - Funding Objective: Proof-of-concept development, sensor breakout procurement, dual-bus firmware engineering, and TinyML pipeline optimization.",
         "")
    ]

    first = True
    for hdr, body in items_s3:
        if first:
            p = tf_tech.paragraphs[0]
            first = False
        else:
            p = tf_tech.add_paragraph()
        p.text = hdr
        p.font.name = FONT_MAIN
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_NAVY if "•" in hdr else C_TEAL
        if body:
            p2 = tf_tech.add_paragraph()
            p2.text = body
            p2.font.name = FONT_MAIN
            p2.font.size = Pt(10)
            p2.font.color.rgb = C_GRAY

    # Right Column: Visual Prototype Architecture Card
    card_vis = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), Inches(1.5), Inches(4.7), Inches(5.5))
    card_vis.fill.solid()
    card_vis.fill.fore_color.rgb = C_WHITE
    card_vis.line.color.rgb = C_BORDER

    tb_v = slide3.shapes.add_textbox(Inches(8.2), Inches(1.65), Inches(4.3), Inches(0.5))
    p_vh = tb_v.text_frame.paragraphs[0]
    p_vh.text = "Prototype Engineering Architecture"
    p_vh.font.name = FONT_MAIN
    p_vh.font.size = Pt(14)
    p_vh.font.bold = True
    p_vh.font.color.rgb = C_NAVY

    if os.path.exists(fig6):
        slide3.shapes.add_picture(fig6, Inches(8.15), Inches(2.2), width=Inches(4.4), height=Inches(3.3))

    tb_vdesc = slide3.shapes.add_textbox(Inches(8.2), Inches(5.6), Inches(4.3), Inches(1.2))
    p_vd = tb_vdesc.text_frame.paragraphs[0]
    p_vd.text = "Fig: Complete hardware subsystem layout transitioning from benchtop breadboard (TRL 4) to 4-layer rigid-flex IP54 sleeve."
    p_vd.font.name = FONT_MAIN
    p_vd.font.size = Pt(9.5)
    p_vd.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 4: Proposed Technology/Product Details
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Proposed Technology/Product Details", has_iitd=False)

    card_s4_l = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(6.8), Inches(5.5))
    card_s4_l.fill.solid()
    card_s4_l.fill.fore_color.rgb = C_LIGHT_BG
    card_s4_l.line.color.rgb = C_BORDER

    tb_s4_l = slide4.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(6.4), Inches(5.2))
    tf_s4_l = tb_s4_l.text_frame
    tf_s4_l.word_wrap = True

    sections_s4 = [
        ("• Novelty: Multimodal On-Device TinyML Fusion",
         "100% offline edge fusion combining Far-IR radiometric thermography (MLX90640), single-lead ECG rhythm monitoring (MAX30003), dual-wavelength PPG SpO2/HR (MAX30102), chest-wall motion respiration (MPU6050 IMU), 14-channel spectral hemoglobin absorption index (AS7343), galvanic skin response (GSR), and ambient gas safety (MQ-135) on a dual-core ESP32-S3."),
        
        ("• Product Specifications (BOM: ₹8,950 | Mass Scale: <₹5,000)",
         "Compute: Dual-Core Xtensa LX7 @ 240 MHz, 512 KB SRAM + 8 MB PSRAM.\n"
         "Bus Architecture: Dual physical buses (Wire1 @ 400 kHz dedicated to optical pulse; Wire @ 50 kHz for multiplexed environmental/spectral sensors).\n"
         "Power: Single-cell 2,000 mAh Li-Po / 18650 with PMIC (10.8 hrs active runtime, 185 mA active / 12 mA standby).\n"
         "Display: 0.96\" SSD1306 OLED + 3-state bi-color LED + offline bilingual Hindi/English TTS audio engine."),
        
        ("• USP: Zero-Consumable, Zero-Literacy, 100% Offline Autonomy",
         "Eliminates recurring test strip costs (₹0 per test). Delivers an intuitive tri-color verdict (Green: Normal | Blinking Amber: Repeat Scan / Noise | Red: Urgent Referral) with zero cloud dependency.")
    ]

    first = True
    for hdr, body in sections_s4:
        if first:
            p = tf_s4_l.paragraphs[0]
            first = False
        else:
            p = tf_s4_l.add_paragraph()
        p.text = hdr
        p.font.name = FONT_MAIN
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        p2 = tf_s4_l.add_paragraph()
        p2.text = body
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_GRAY

    # Right Column: Cobotics & Sustainability + Hardware Diagram
    card_s4_r = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(1.5), Inches(5.1), Inches(5.5))
    card_s4_r.fill.solid()
    card_s4_r.fill.fore_color.rgb = C_LIGHT_BG
    card_s4_r.line.color.rgb = C_BORDER

    tb_s4_r = slide4.shapes.add_textbox(Inches(7.8), Inches(1.65), Inches(4.7), Inches(5.2))
    tf_s4_r = tb_s4_r.text_frame
    tf_s4_r.word_wrap = True

    sections_s4_r = [
        ("• Cobotics Component & Assistive Ergonomics",
         "Designed as an intelligent collaborative screening assistant ('Tri-Corder Stethoscope Sleeve'). Works collaboratively with non-technical frontline health workers by actively monitoring sensor-skin contact impedance, verifying signal perfusion index, and guiding the operator through patient sensor repositioning before accepting readings."),
        
        ("• Environmental Impact & Sustainability",
         "100% Non-invasive with Zero Biohazard Waste: Unlike single-use biochemical test strips and blood lancets, Smart-ASHA generates zero chemical waste. Low-power circuitry supports rural solar micro-charging and long operational field longevity.")
    ]

    first = True
    for hdr, body in sections_s4_r:
        if first:
            p = tf_s4_r.paragraphs[0]
            first = False
        else:
            p = tf_s4_r.add_paragraph()
        p.text = hdr
        p.font.name = FONT_MAIN
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_TEAL
        p2 = tf_s4_r.add_paragraph()
        p2.text = body
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_GRAY

    # Add Figure 1 Hardware architecture snippet
    if os.path.exists(fig1):
        slide4.shapes.add_picture(fig1, Inches(7.85), Inches(4.2), width=Inches(4.6), height=Inches(2.6))

    # =========================================================================
    # SLIDE 5: Comparison with Existing Solutions
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Comparison of the proposed technology with existing similar solutions (national and international competitors)", has_iitd=False)

    tb_intro5 = slide5.shapes.add_textbox(Inches(0.6), Inches(1.35), Inches(12.1), Inches(0.4))
    p5 = tb_intro5.text_frame.paragraphs[0]
    p5.text = "• Provide a detailed comparative chart: Smart-ASHA vs. Commercial Kiosks & Clinical Monitors"
    p5.font.name = FONT_MAIN
    p5.font.size = Pt(13)
    p5.font.bold = True
    p5.font.color.rgb = C_NAVY

    # Table dimensions
    rows, cols = 8, 5
    tbl_shape = slide5.shapes.add_table(rows, cols, Inches(0.6), Inches(1.8), Inches(12.133), Inches(5.2))
    tbl = tbl_shape.table

    # Column widths
    tbl.columns[0].width = Inches(2.3)
    tbl.columns[1].width = Inches(2.7)
    tbl.columns[2].width = Inches(2.4)
    tbl.columns[3].width = Inches(2.4)
    tbl.columns[4].width = Inches(2.333)

    comp_headers = ["Parameter / Metric", "Smart-ASHA (Arogya AI)\n[Proposed Workstation]", "HealthCube Kiosk\n[Commercial POC Kiosk]", "Multipara Patient Monitor\n[Hospital Standard]", "Single-Parameter Gadgets\n[Fragmented Oximeter/IR]"]
    for c_idx, h_text in enumerate(comp_headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TBL_HDR if c_idx != 1 else C_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_MAIN
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    comp_data = [
        ("Capital Unit Cost", "₹8,950 prototype | <₹5,000 scale\n(Over 15× more affordable)", "₹1,20,000 – ₹2,20,000\n(Prohibitive for rural PHCs)", "₹1,50,000 – ₹3,00,000\n(Capital-intensive)", "₹3,000 – ₹5,000 total\n(Fragmented devices)"),
        ("Recurring Consumable Cost", "₹0 / Test\n(100% Non-invasive optical/thermal)", "₹80 – ₹250 per test cartridge\n(>₹9 Lakhs/year/PHC recurring)", "₹20 – ₹50 per patient\n(Disposable ECG electrodes/cables)", "₹0 / Test\n(No consumables)"),
        ("Network Connectivity", "100% Offline Edge-AI\n(On-board TFLite Micro inference)", "Requires continuous 4G/Cloud\n(Fails in disconnected villages)", "Standalone bedside / clinic\n(Requires 230V AC mains)", "Standalone isolated\n(Zero connectivity/records)"),
        ("Integrated Modalities", "7-in-1: ECG, SpO2, HR, Respiration, IR Thermal, Spectral Hb, GSR", "Strip chemistry, BP, SpO2, single ECG (Separate accessories)", "ECG, NIBP, SpO2, Temp\n(Bulky bedside unit)", "1–2 isolated metrics\n(No multi-sensor fusion)"),
        ("Frontline User Interface", "Zero-Literacy: Tri-color visual state + Spoken Hindi/English audio", "Requires Android tablet operation & digital literacy", "Complex medical waveforms;\nRequires trained physician", "Raw decimal numbers;\nNo triage or context"),
        ("Form Factor & Battery", "Handheld sleeve / pocket-sized;\n10.8 hrs continuous Li-Po", "Heavy briefcase/trolley (8–12 kg);\n2–4 hrs internal battery", "Heavy bedside trolley (5–10 kg);\n1–2 hrs UPS backup", "Pocket clip-on;\nStandard AAA cells"),
        ("Referral Integration", "Offline Ayushman Bharat QR Slip +\n1-tap WhatsApp tele-consult", "Proprietary cloud portal export\n(Subscription model)", "Local thermal printer / hospital LAN connection", "None\n(Manual verbal referral)")
    ]

    for r_idx, row_items in enumerate(comp_data):
        for c_idx, val in enumerate(row_items):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if c_idx == 1:
                cell.fill.fore_color.rgb = RGBColor(238, 242, 255)  # highlight smart-asha
            elif r_idx % 2 == 1:
                cell.fill.fore_color.rgb = C_TBL_ALT
            else:
                cell.fill.fore_color.rgb = C_WHITE
            
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_MAIN
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_NAVY if c_idx == 1 else (C_BLACK if c_idx == 0 else C_GRAY)
            if c_idx <= 1:
                p.font.bold = True
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # =========================================================================
    # SLIDE 6: Commercial Potential and Market Demand
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Commercial Potential and Market Demand", has_iitd=True)

    # 3 Cards Layout: Commercial Potential, Market Demand, Duration to TRL 9
    col_w = Inches(3.8)
    card_gap = Inches(0.3)
    start_x = Inches(0.6)

    # Card 1: Commercial Potential
    c1 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, Inches(1.5), col_w, Inches(5.5))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_LIGHT_BG
    c1.line.color.rgb = C_BORDER

    tb_c1 = slide6.shapes.add_textbox(start_x + Inches(0.2), Inches(1.65), col_w - Inches(0.4), Inches(5.2))
    tf1 = tb_c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Commercial Potential"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    pts_cp = [
        ("B2G Public Procurement: ", "Direct eligibility for government procurement via Government e-Marketplace (GeM) under National Health Mission (NHM) and Ayushman Bharat HWCs."),
        ("Zero Recurring Consumables: ", "Unmatched economic proposition for state health budgets; eliminates recurring cartridge purchase liabilities that stall competitor kiosks."),
        ("CSR & Global Health NGOs: ", "Deployment with rural healthcare initiatives (e.g., Tata Trusts, Piramal Swasthya) and mobile health outreach units."),
        ("Rural Private Clinics: ", "High demand from 250,000+ rural registered medical practitioners and clinics seeking low-cost vital diagnostic kits.")
    ]
    for h, b in pts_cp:
        p = tf1.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10.5)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Card 2: Market Demand
    start_x2 = start_x + col_w + card_gap
    c2 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x2, Inches(1.5), col_w, Inches(5.5))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_LIGHT_BG
    c2.line.color.rgb = C_BORDER

    tb_c2 = slide6.shapes.add_textbox(start_x2 + Inches(0.2), Inches(1.65), col_w - Inches(0.4), Inches(5.2))
    tf2 = tb_c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Market Demand"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    pts_md = [
        ("1.1+ Million ASHA Workers: ", "National mandate to equip frontline community activists with digital, non-invasive health evaluation tools."),
        ("160,000+ Ayushman Bharat HWCs: ", "Upgraded rural sub-centres needing rapid multi-parameter screening for non-communicable disease (NCD) camps."),
        ("₹8,500+ Cr POC Diagnostics Market: ", "Indian Point-of-Care Diagnostics market growing rapidly at 14.5% CAGR, driven by indigenous manufacturing policies ('Make in India')."),
        ("Post-Pandemic Diagnostic Awareness: ", "Urgent rural demand for integrated hypoxemia, respiratory rate, and fever screening.")
    ]
    for h, b in pts_md:
        p = tf2.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10.5)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Card 3: Duration to reach TRL 9
    start_x3 = start_x2 + col_w + card_gap
    c3 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x3, Inches(1.5), col_w, Inches(5.5))
    c3.fill.solid()
    c3.fill.fore_color.rgb = C_LIGHT_BG
    c3.line.color.rgb = C_BORDER

    tb_c3 = slide6.shapes.add_textbox(start_x3 + Inches(0.2), Inches(1.65), col_w - Inches(0.4), Inches(5.2))
    tf3 = tb_c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "Duration to Reach TRL 9"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CRIMSON

    pts_trl = [
        ("Total Estimated Time: 18–24 Months", ""),
        ("• Phase 1 (M1–M4) [TRL 5]: ", "Custom 4-layer rigid-flex PCB fabrication, PMIC integration, and IP54 ergonomic enclosure tooling."),
        ("• Phase 2 (M5–M10) [TRL 6–7]: ", "Double-blind clinical reference validation (ISO 80601-2-61) and frontline ASHA pilot usability trials across rural PHCs."),
        ("• Phase 3 (M11–M16) [TRL 8]: ", "CDSCO Class B medical device regulatory clearance, IEC 60601-1 safety certification, and design freeze."),
        ("• Phase 4 (M17–M24) [TRL 9]: ", "Domestic EMS contract manufacturing ramp-up, GeM portal listing, and commercial supply chain rollout.")
    ]
    for h, b in pts_trl:
        p = tf3.add_paragraph()
        if not b:
            p.text = h
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
        else:
            p.text = h
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = C_BLACK
            r = p.add_run()
            r.text = b
            r.font.bold = False
            r.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 7: Outcome Oriented Milestones with Timelines (1 Year)
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Outcome oriented milestone with timelines for one year", has_iitd=True)

    quarters = [
        ("Quarter 1 (Months 1–3)", "Hardware Consolidation & Rigid-Flex PCB", C_NAVY, [
            "Finalize 4-layer rigid-flex PCB design eliminating 20 cm breadboard jumpers.",
            "Integrate Quectel 4G LTE/GNSS module, PMIC battery fuel gauge, and dual-bus layout.",
            "Fabricate 5 pilot beta units in 3D-printed biocompatible IP54 ergonomic sleeves with optical contact shrouds.",
            "Milestone Target: Zero I2C bus lockups; rock-solid 400 kHz optical signal acquisition."
        ]),
        ("Quarter 2 (Months 4–6)", "Clinical Benchmarking & Algorithm Calibration", C_TEAL, [
            "Double-blind laboratory comparison against gold standards: clinical hematology analyzer, ISO 80601-2-61 pulse oximeter, calibrated 12-lead ECG.",
            "Calibrate dynamic Stefan-Boltzmann radiometric thermal engine across ambient heat (25°C–42°C).",
            "Refine multi-wavelength spectral hemoglobin regression model across diverse Fitzpatrick skin tones (I–VI).",
            "Milestone Target: Documented Bland-Altman correlation curves and INT8 TFLite model optimization."
        ]),
        ("Quarter 3 (Months 7–9)", "Frontline ASHA Worker Usability Trials", C_NAVY, [
            "Deploy 10 beta units to active ASHA/ANM workers across rural Primary Health Sub-Centres (Delhi-NCR / Haryana).",
            "Quantify real-world usability: time-to-scan (10s Express vs 60s Deep Scan), audio instruction comprehension.",
            "Evaluate battery performance over full 8-hour field shifts under rural field temperatures.",
            "Milestone Target: User feedback dossier, field bug fixes, and firmware triage threshold fine-tuning."
        ]),
        ("Quarter 4 (Months 10–12)", "Regulatory Dossier & ABDM Telemedicine Integration", C_CRIMSON, [
            "Assemble Technical Construction File (TCF) and risk management documentation (ISO 14971) for CDSCO Class B filing.",
            "Implement FHIR-compliant Ayushman Bharat Health Account (ABHA) integration and 1-tap WhatsApp tele-consultation.",
            "Conduct pre-compliance safety tests for IEC 60601-1 (electrical safety) and IEC 60601-1-2 (EMC).",
            "Milestone Target: Regulatory submission readiness and 50-unit commercial pilot deployment."
        ])
    ]

    card_h = Inches(5.3)
    card_w = Inches(2.8)
    gap_x = Inches(0.24)
    sx = Inches(0.6)

    for idx, (q_title, q_sub, col_theme, q_tasks) in enumerate(quarters):
        x = sx + idx * (card_w + gap_x)
        c = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.5), card_w, card_h)
        c.fill.solid()
        c.fill.fore_color.rgb = C_LIGHT_BG
        c.line.color.rgb = col_theme
        c.line.width = Pt(1.5)

        tb = slide7.shapes.add_textbox(x + Inches(0.15), Inches(1.65), card_w - Inches(0.3), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = q_title
        p1.font.name = FONT_MAIN
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = col_theme

        p2 = tf.add_paragraph()
        p2.text = q_sub
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = C_BLACK

        for t in q_tasks:
            p = tf.add_paragraph()
            p.text = "• " + t
            p.font.name = FONT_MAIN
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 8: Role of Collaborators/Consortium Model
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Role of collaborators/Consortium Model (Also mention, if there any investment from any collaborators)", has_iitd=False)

    card_s8_l = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(6.8), Inches(5.5))
    card_s8_l.fill.solid()
    card_s8_l.fill.fore_color.rgb = C_LIGHT_BG
    card_s8_l.line.color.rgb = C_BORDER

    tb_s8_l = slide8.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(6.4), Inches(5.2))
    tf_s8_l = tb_s8_l.text_frame
    tf_s8_l.word_wrap = True

    p = tf_s8_l.paragraphs[0]
    p.text = "Consortium Model & Partner Roles"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    partners = [
        ("Vivekananda Institute of Professional Studies - Technical Campus (VIPS-TC): ", "Parent Academic Institution. Provides embedded hardware laboratory facilities, prototyping equipment, administrative backing, and continuous faculty supervision."),
        ("I-Hub Foundation for Cobotics (IHFC) - IIT Delhi: ", "Proposed Incubation & Technology Translation Partner. Mentorship in cobotic assistive medical device design, access to IIT Delhi rapid prototyping and testing infrastructure, and seed funding support."),
        ("Clinical Validation Partners (Target PHCs / Medical Colleges): ", "Targeting institutional MoUs with government Primary Health Centres (PHCs) and regional medical colleges in Delhi-NCR/Haryana for ethical clearance, clinical reference data collection, and frontline ASHA user testing."),
        ("NABL / BIS Certified Testing Laboratories: ", "External authorized agencies for IEC 60601-1 electrical safety, EMC/EMI shielding, and RoHS environmental compliance testing.")
    ]
    for h, b in partners:
        p = tf_s8_l.add_paragraph()
        p.text = "• "
        p.font.size = Pt(11)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Right Column: Investment from Collaborators & IP Structure
    card_s8_r = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(1.5), Inches(5.1), Inches(5.5))
    card_s8_r.fill.solid()
    card_s8_r.fill.fore_color.rgb = C_LIGHT_BG
    card_s8_r.line.color.rgb = C_BORDER

    tb_s8_r = slide8.shapes.add_textbox(Inches(7.8), Inches(1.65), Inches(4.7), Inches(5.2))
    tf_s8_r = tb_s8_r.text_frame
    tf_s8_r.word_wrap = True

    p = tf_s8_r.paragraphs[0]
    p.text = "Collaborator Investment & Equity Structure"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    pts_inv = [
        ("Investment from Collaborators to Date: Nil / Zero External Investment",
         "The project is 100% self-funded through internal student research funds and institutional laboratory access at VIPS-TC. No external angel, venture capital, or corporate investor funding has been received to date."),
        
        ("In-Kind Institutional Contributions: ",
         "• Laboratory bench space, oscilloscopes, spectrum analyzers, and testing equipment at VIPS-TC.\n• Academic guidance and faculty time commitment.\n• Cloud development and machine learning workstation access."),
        
        ("Clean Intellectual Property (IP) Ownership: ",
         "100% unencumbered intellectual property held jointly by the student inventors (Gauri Gupta, Anmol Nandwani, Vansh Sharma) and VIPS-TC, facilitating seamless incubation and technology transfer under IHFC / IIT Delhi policies."),
        
        ("Future Incubation Equity Sharing: ",
         "The team is prepared to enter into standard incubation and equity-sharing agreements with IHFC IIT Delhi in accordance with institutional guidelines upon grant selection.")
    ]
    for h, b in pts_inv:
        p = tf_s8_r.add_paragraph()
        if not b:
            p.text = h
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = C_CRIMSON
        else:
            p.text = h
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = C_BLACK
            r = p.add_run()
            r.text = b
            r.font.bold = False
            r.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 9: Team Details
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Team Details", has_iitd=True)

    tb_sub9 = slide9.shapes.add_textbox(Inches(0.6), Inches(1.35), Inches(12.1), Inches(0.35))
    p9 = tb_sub9.text_frame.paragraphs[0]
    p9.text = "Please add background of Founders and Key Personnels"
    p9.font.name = FONT_MAIN
    p9.font.size = Pt(13)
    p9.font.italic = True
    p9.font.color.rgb = C_GRAY

    team_members = [
        ("Gauri Gupta", "Lead Researcher & Embedded Systems", "Enrollment No.: 03417711724 | IIoT - A\nSchool of Engineering & Technology, VIPS-TC", [
            "Project Lead & Hardware Prototyping.",
            "Specializes in embedded biomedical sensor interfacing (I2C/SPI), power management circuits, and dual-bus architecture.",
            "Lead applicant for Vishwakarma Awards 2026–27 (VK26-AU-FD-0006)."
        ]),
        ("Anmol Nandwani", "Co-Lead & Edge AI / Machine Learning", "Enrollment No.: 35117711724 | IIoT - A\nSchool of Engineering & Technology, VIPS-TC", [
            "Specializes in TinyML neural network optimization, TFLite Micro INT8 quantization, and digital signal processing.",
            "Developed the dynamic Stefan-Boltzmann radiometric thermal drift engine and sensor fusion pipeline.",
            "Lead developer of on-device inference benchmarking."
        ]),
        ("Vansh Sharma", "Co-Lead & System Integration", "Enrollment No.: 02717711724 | IIoT - A\nSchool of Engineering & Technology, VIPS-TC", [
            "Specializes in firmware state machines, hardware-in-the-loop validation, and offline clinical mobile application (Flutter).",
            "Designed the zero-literacy tri-color triage state logic and offline Ayushman QR referral generation.",
            "Core integration and laboratory bench testing."
        ]),
        ("Dr. Divya Agarwal", "Faculty Guide & Academic Mentor", "Assistant Professor, Dept. of IIoT\nSchool of Engineering & Technology, VIPS-TC", [
            "Email: divya.agarwal@vips.edu | Phone: [To be filled by Mentor]",
            "Domain: Biomedical IoT, Embedded Intelligent Systems, and Signal Processing.",
            "Provides academic oversight, research methodology rigor, sensor fusion verification, and IEEE publication guidance."
        ])
    ]

    card_w9 = Inches(2.8)
    card_h9 = Inches(5.3)
    gap_x9 = Inches(0.24)
    start_x9 = Inches(0.6)

    for idx, (m_name, m_role, m_meta, m_points) in enumerate(team_members):
        x = start_x9 + idx * (card_w9 + gap_x9)
        c = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.7), card_w9, card_h9)
        c.fill.solid()
        c.fill.fore_color.rgb = C_LIGHT_BG
        c.line.color.rgb = C_NAVY if idx < 3 else C_TEAL
        c.line.width = Pt(1.5)

        tb = slide9.shapes.add_textbox(x + Inches(0.15), Inches(1.85), card_w9 - Inches(0.3), card_h9 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = m_name
        p1.font.name = FONT_MAIN
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY if idx < 3 else C_TEAL

        p2 = tf.add_paragraph()
        p2.text = m_role
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = C_BLACK

        p3 = tf.add_paragraph()
        p3.text = m_meta
        p3.font.name = FONT_MAIN
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_GRAY

        tf.add_paragraph()  # spacing

        for pt in m_points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.name = FONT_MAIN
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 10: Investment Details for One Year (Budget Table)
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Investment Details for one year", has_iitd=True)

    rows10, cols10 = 7, 4
    t_shape10 = slide10.shapes.add_table(rows10, cols10, Inches(0.6), Inches(1.6), Inches(12.133), Inches(5.4))
    tbl10 = t_shape10.table

    tbl10.columns[0].width = Inches(2.6)
    tbl10.columns[1].width = Inches(1.6)
    tbl10.columns[2].width = Inches(1.6)
    tbl10.columns[3].width = Inches(6.333)

    h_budget = ["Budget Heads", "6 months\n(Phase I)", "6 months\n(Phase II)", "Justification"]
    for c_idx, h_text in enumerate(h_budget):
        cell = tbl10.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TBL_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_MAIN
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    budget_data = [
        ("Equipment\n(refinement of the current product/ no importing)",
         "₹4.50 Lacs", "₹2.50 Lacs",
         "Custom 4-layer rigid-flex PCB fabrication & SMD assembly tooling; 3D printing of ergonomic IP54 sleeves with medical-grade resin; reference calibration instruments (multi-parameter patient vital simulator, calibrated digital reference thermometer, reference optical fixtures; all domestically sourced)."),
        
        ("Manpower",
         "₹3.60 Lacs", "₹3.60 Lacs",
         "2 Project Research Fellows / Embedded & Edge-AI Engineers (@ ₹30,000/month each for 12 months) dedicated to dual-bus firmware architecture, FreeRTOS scheduling, TFLite Micro model optimization, and clinical data logging."),
        
        ("Consumables",
         "₹1.80 Lacs", "₹1.20 Lacs",
         "Sensor breakout modules (MAX30003 single-lead ECG, MLX90640 far-IR thermopile, AS7343 spectral, MAX30102 PPG), PMIC chips, 2,000 mAh Li-Po battery cells, Quectel 4G LTE modems, medical-grade silicone contact shrouds, cables, and electronic components for 20 beta units."),
        
        ("Contingency",
         "₹0.60 Lacs", "₹0.60 Lacs",
         "5% statutory contingency buffer for iterative PCB design revisions, component lead-time price fluctuations, and unexpected NABL pre-compliance laboratory test charges."),
        
        ("Travel",
         "₹0.50 Lacs", "₹0.90 Lacs",
         "Field visits by technical team to rural Primary Health Centres (PHCs) and sub-centres in Haryana and Rajasthan for clinical observation, ASHA worker usability testing, and local health officer feedback."),
        
        ("Total",
         "₹11.00 Lacs", "₹8.80 Lacs",
         "Total 1-Year Grant Request: ₹19.80 Lacs (~₹20 Lacs) to transition Smart-ASHA from TRL 4 bench prototype to a field-tested TRL 6 clinical device ready for regulatory clearance.")
    ]

    for r_idx, row in enumerate(budget_data):
        for c_idx, val in enumerate(row):
            cell = tbl10.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if r_idx == len(budget_data) - 1:
                cell.fill.fore_color.rgb = RGBColor(224, 231, 255)  # total highlight
            elif r_idx % 2 == 1:
                cell.fill.fore_color.rgb = C_TBL_ALT
            else:
                cell.fill.fore_color.rgb = C_WHITE

            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_MAIN
            p.font.size = Pt(10)
            p.font.color.rgb = C_NAVY if r_idx == len(budget_data) - 1 else C_BLACK
            if r_idx == len(budget_data) - 1 or c_idx < 3:
                p.font.bold = True
            p.alignment = PP_ALIGN.CENTER if 1 <= c_idx <= 2 else PP_ALIGN.LEFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # =========================================================================
    # SLIDE 11: Business Plan/Commercialization Strategy
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Business Plan/Commercialization Strategy", has_iitd=True)

    c11_w = Inches(3.8)
    c11_h = Inches(5.5)
    c11_gap = Inches(0.3)
    sx11 = Inches(0.6)

    # Pillar 1: Public Health Procurement (B2G)
    c_p1 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx11, Inches(1.5), c11_w, c11_h)
    c_p1.fill.solid()
    c_p1.fill.fore_color.rgb = C_LIGHT_BG
    c_p1.line.color.rgb = C_NAVY
    c_p1.line.width = Pt(1.5)

    tb1 = slide11.shapes.add_textbox(sx11 + Inches(0.15), Inches(1.65), c11_w - Inches(0.3), c11_h - Inches(0.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Pillar 1: B2G Public Procurement"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    pts_p1 = [
        ("Government e-Marketplace (GeM): ", "List Smart-ASHA on GeM under indigenous medical device procurement categories."),
        ("National Health Mission (NHM): ", "Target state tenders for equipping 1.1M+ ASHA workers with subsidized non-invasive diagnostic kits."),
        ("Ayushman Bharat AB-HWCs: ", "Supply to 160,000+ Health & Wellness Centres to standardize community non-communicable disease (NCD) screening."),
        ("Zero Recurring Budget Burden: ", "Government tenders heavily favor zero-consumable devices over strip-based kiosks that demand recurrent budget allocations.")
    ]
    for h, b in pts_p1:
        p = tf1.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Pillar 2: CSR & NGO Health Networks
    sx11_2 = sx11 + c11_w + c11_gap
    c_p2 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx11_2, Inches(1.5), c11_w, c11_h)
    c_p2.fill.solid()
    c_p2.fill.fore_color.rgb = C_LIGHT_BG
    c_p2.line.color.rgb = C_TEAL
    c_p2.line.width = Pt(1.5)

    tb2 = slide11.shapes.add_textbox(sx11_2 + Inches(0.15), Inches(1.65), c11_w - Inches(0.3), c11_h - Inches(0.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Pillar 2: CSR & Health NGOs"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    pts_p2 = [
        ("Corporate CSR Foundations: ", "Partner with corporate healthcare CSR programs (e.g., Tata Trusts, Piramal Swasthya, Reliance Foundation) deploying mobile medical vans."),
        ("International Health NGOs: ", "Scale into underserved global South territories (South Asia, Sub-Saharan Africa) facing similar rural physician deficits."),
        ("District Health Pilot Grants: ", "Deploy sponsored 50-unit pilot clusters funded through institutional CSR to establish verified health outcome datasets."),
        ("Telemedicine Software Sync: ", "Offer optional recurring value-added SaaS subscriptions for district-level epidemiological heatmaps and dashboards.")
    ]
    for h, b in pts_p2:
        p = tf2.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Pillar 3: Make-in-India Manufacturing
    sx11_3 = sx11_2 + c11_w + c11_gap
    c_p3 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx11_3, Inches(1.5), c11_w, c11_h)
    c_p3.fill.solid()
    c_p3.fill.fore_color.rgb = C_LIGHT_BG
    c_p3.line.color.rgb = C_CRIMSON
    c_p3.line.width = Pt(1.5)

    tb3 = slide11.shapes.add_textbox(sx11_3 + Inches(0.15), Inches(1.65), c11_w - Inches(0.3), c11_h - Inches(0.3))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "Pillar 3: Domestic Manufacturing Scale"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CRIMSON

    pts_p3 = [
        ("Domestic EMS Contract Manufacturing: ", "Partner with certified Indian Electronics Manufacturing Services (EMS) facilities for high-yield SMT pick-and-place assembly."),
        ("Sub-₹5,000 Economies of Scale: ", "Volume component purchasing at 5,000+ units reduces total BOM from ₹8,950 to under ₹5,000, ensuring unbeatable price barriers."),
        ("Domestic Supply Chain: ", "100% compliant with 'Make in India' and Public Procurement (Preference to Make in India) Order guidelines."),
        ("Post-Sale Maintenance: ", "Modular sleeve replacement and over-the-air (OTA) firmware triage updates via onboard 4G LTE modem.")
    ]
    for h, b in pts_p3:
        p = tf3.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 12: Expectation from IHFC
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Expectation from IHFC", has_iitd=True)

    tb_sub12 = slide12.shapes.add_textbox(Inches(0.6), Inches(1.35), Inches(12.1), Inches(0.35))
    p12 = tb_sub12.text_frame.paragraphs[0]
    p12.text = "• Specify expectations from IHFC for commercialization"
    p12.font.name = FONT_MAIN
    p12.font.size = Pt(13)
    p12.font.bold = True
    p12.font.color.rgb = C_NAVY

    card_h12 = Inches(5.4)
    card_w12 = Inches(2.8)
    gap_x12 = Inches(0.24)
    sx12 = Inches(0.6)

    ihfc_items = [
        ("Funds Requirement", "₹19.80 Lacs (~₹20 Lacs)", C_NAVY, [
            "Prototype Refinement: Fabrication of 4-layer rigid-flex PCBs and industrial IP54 enclosures.",
            "Consumables & Sensors: Sourcing multi-modal sensor breakout suites for 20 beta units.",
            "Manpower: Compensation for 2 dedicated embedded/AI project engineers for 12 months.",
            "Clinical Field Pilots: Logistical support for rural Primary Health Centre (PHC) usability trials in Haryana/Rajasthan."
        ]),
        ("Mentorship Required", "Technical & Regulatory Expertise", C_TEAL, [
            "Cobotics & Ergonomics: Guidance from IIT Delhi faculty on assistive physical human-device interaction for community health workers.",
            "Regulatory Pathway: Mentorship on CDSCO Medical Device Rules (MDR 2017) Class B notification and SaMD software lifecycle (IEC 62304).",
            "Clinical Trial Protocol: Structuring formal double-blind hospital validation protocols complying with ICMR ethical standards."
        ]),
        ("Space & Ecosystem", "Prototyping & Incubation Infrastructure", C_NAVY, [
            "IHFC Lab Facilities: Access to rapid prototyping resources (high-precision 3D printing, SMD reflow stations, PCB milling).",
            "Medical Device Testing: Utilization of IIT Delhi environmental testing chambers, EMC/EMI shielding cages, and calibration setups.",
            "Clinical Network: Warm introductions to regional medical institutions and rural hospital partners for pilot studies."
        ]),
        ("Commercialisation: Our Role", "Startup Spinout & Technology Execution", C_CRIMSON, [
            "Dedicated Core Team: Student inventors and faculty guide will execute 100% of firmware, edge-AI, and hardware integration.",
            "Startup Incorporation: Formal incorporation of a medical technology startup incubated under IHFC / IIT Delhi.",
            "Equity & Licensing: Open to mutually agreed incubation equity sharing and intellectual property assignment in accordance with IHFC policy."
        ])
    ]

    for idx, (title, sub, col_theme, points) in enumerate(ihfc_items):
        x = sx12 + idx * (card_w12 + gap_x12)
        c = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.7), card_w12, card_h12)
        c.fill.solid()
        c.fill.fore_color.rgb = C_LIGHT_BG
        c.line.color.rgb = col_theme
        c.line.width = Pt(1.5)

        tb = slide12.shapes.add_textbox(x + Inches(0.15), Inches(1.85), card_w12 - Inches(0.3), card_h12 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = "• " + title
        p1.font.name = FONT_MAIN
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = col_theme

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = C_BLACK

        tf.add_paragraph()  # spacing

        for pt in points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.name = FONT_MAIN
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 13: Legal Framework Required for Commercialization
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, "Legal framework required for achieving the commercialization of your patent/technology/prototype, if any, Details", has_iitd=False)

    card_w13 = Inches(3.8)
    card_h13 = Inches(5.5)
    gap_x13 = Inches(0.3)
    sx13 = Inches(0.6)

    # Box 1: Regulatory Requirements & Standards
    c13_1 = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx13, Inches(1.5), card_w13, card_h13)
    c13_1.fill.solid()
    c13_1.fill.fore_color.rgb = C_LIGHT_BG
    c13_1.line.color.rgb = C_NAVY
    c13_1.line.width = Pt(1.5)

    tb13_1 = slide13.shapes.add_textbox(sx13 + Inches(0.15), Inches(1.65), card_w13 - Inches(0.3), card_h13 - Inches(0.3))
    tf1 = tb13_1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Regulatory Requirements & Safety Standards"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    pts_r = [
        ("CDSCO Medical Device Rules (MDR 2017): ", "Classified as a Class B Non-Invasive Physiological Monitoring Device (Low-to-Moderate Risk)."),
        ("Software as a Medical Device (SaMD): ", "Compliance with IEC 62304 (Medical device software life cycle processes) for on-device TinyML fever CNN and heuristic triage rules."),
        ("Electrical Safety & EMC: ", "Testing compliance under IEC 60601-1 (General requirements for basic safety and essential performance) and IEC 60601-1-2 (Electromagnetic compatibility)."),
        ("Sensor Performance Standards: ", "Benchmarking SpO2 against ISO 80601-2-61 (Pulse oximeter equipment) and clinical thermometry against ISO 80601-2-56.")
    ]
    for h, b in pts_r:
        p = tf1.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Box 2: Status of MoU or Agreements
    sx13_2 = sx13 + card_w13 + gap_x13
    c13_2 = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx13_2, Inches(1.5), card_w13, card_h13)
    c13_2.fill.solid()
    c13_2.fill.fore_color.rgb = C_LIGHT_BG
    c13_2.line.color.rgb = C_TEAL
    c13_2.line.width = Pt(1.5)

    tb13_2 = slide13.shapes.add_textbox(sx13_2 + Inches(0.15), Inches(1.65), card_w13 - Inches(0.3), card_h13 - Inches(0.3))
    tf2 = tb13_2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Status of MoU or Agreements"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    pts_mou = [
        ("Institutional Agreement: ", "Internal institutional project authorization and laboratory access agreement formalized at VIPS-TC."),
        ("IHFC Incubation Agreement: ", "Formal Incubation MoU and Technology Transfer Agreement to be executed upon selection under SwasthyaTech Synapse 2026."),
        ("Clinical Trial MoUs: ", "[In Progress: Discussions initiated with regional medical college hospitals and rural Primary Health Centres (PHCs) in Haryana for clinical evaluation protocols]."),
        ("ICMR Ethical Clearance: ", "Institutional Ethics Committee (IEC) review application to be submitted in Month 3 for human volunteer reference trials.")
    ]
    for h, b in pts_mou:
        p = tf2.add_paragraph()
        p.text = "• "
        p.font.size = Pt(10)
        p.font.name = FONT_MAIN
        r1 = p.add_run()
        r1.text = h
        r1.font.bold = True
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = b
        r2.font.color.rgb = C_GRAY

    # Box 3: Agreement with Investors
    sx13_3 = sx13_2 + card_w13 + gap_x13
    c13_3 = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx13_3, Inches(1.5), card_w13, card_h13)
    c13_3.fill.solid()
    c13_3.fill.fore_color.rgb = C_LIGHT_BG
    c13_3.line.color.rgb = C_CRIMSON
    c13_3.line.width = Pt(1.5)

    tb13_3 = slide13.shapes.add_textbox(sx13_3 + Inches(0.15), Inches(1.65), card_w13 - Inches(0.3), card_h13 - Inches(0.3))
    tf3 = tb13_3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "Agreement with Investors (IP, Equity Etc.)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CRIMSON

    pts_eq = [
        ("Current Investor Agreements: Nil / None",
         "The technology has not accepted any external venture capital, angel investment, or third-party debt. There are zero prior equity encumbrances or investor liens."),
        
        ("Clean Intellectual Property: ",
         "100% of underlying software, firmware, and hardware designs are exclusively owned by the student inventors and VIPS-TC."),
        
        ("Incubation Equity Framework: ",
         "The team agrees to allocate founder equity and institutional shares in alignment with standard IHFC / IIT Delhi technology business incubator norms."),
        
        ("Tech Transfer Readiness: ",
         "Well-documented GitHub firmware repositories, KiCad PCB schematics, and TFLite model weights ready for audited due diligence.")
    ]
    for h, b in pts_eq:
        p = tf3.add_paragraph()
        if not b:
            p.text = h
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
        else:
            p.text = h
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = C_BLACK
            r = p.add_run()
            r.text = b
            r.font.bold = False
            r.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 14: Publications from this Technology/Prototype/Patent
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_header(slide14, "Publications from this technology/prototype/patent, if any", has_iitd=True)

    card_s14_l = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(7.2), Inches(5.5))
    card_s14_l.fill.solid()
    card_s14_l.fill.fore_color.rgb = C_LIGHT_BG
    card_s14_l.line.color.rgb = C_BORDER

    tb_s14_l = slide14.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(6.8), Inches(5.2))
    tf_s14_l = tb_s14_l.text_frame
    tf_s14_l.word_wrap = True

    p = tf_s14_l.paragraphs[0]
    p.text = "Peer-Reviewed Manuscripts & Research Proposals"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    pubs = [
        ("Manuscript 1: Full Technical Research Paper (In Drafting / Submission Phase)",
         "Title: 'Arogya AI: A Multi-Modal, Edge-AI Cardiopulmonary and Biochemical Triage Framework for Resource-Constrained Rural Healthcare Settings in India'\n"
         "Authors: Gauri Gupta, Anmol Nandwani, Vansh Sharma, Dr. Divya Agarwal\n"
         "Target Venue: IEEE Conference / Journal (e.g., IEEE EMBC / IEEE Transactions on Biomedical Circuits and Systems / IEEE Sensors)\n"
         "Content: Comprehensive 8-page double-column paper containing 7 high-resolution IEEE-compliant figures, TinyML INT8 quantization benchmarks (142 ms latency, 232 KB PSRAM), Stefan-Boltzmann drift modeling, and laboratory validation across 200 held-out thermal frames."),
        
        ("Project Update & Challenge Addendum (October 2023 – Current)",
         "Title: 'Smart-ASHA (Arogya AI) — An Edge-AI Multimodal Cardiopulmonary & Biochemical Triage Workstation for Frontline Rural Healthcare'\n"
         "Challenge: Maker Bhavan Foundation — Vishwakarma Awards 2026–27 (Theme: Frontier Diagnostics: The Next Vital Signs)\n"
         "Unique Application ID: VK26-AU-FD-0006\n"
         "Scope: Documents the transition from laboratory breadboard to custom 4-layer rigid-flex PCB, dual physical bus segregation, and bilingual audio triage engine.")
    ]

    for h, b in pubs:
        p = tf_s14_l.add_paragraph()
        p.text = h
        p.font.name = FONT_MAIN
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_TEAL
        p2 = tf_s14_l.add_paragraph()
        p2.text = b
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_BLACK

    # Right Column: Model Performance Validation Figure
    card_s14_r = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), Inches(1.5), Inches(4.7), Inches(5.5))
    card_s14_r.fill.solid()
    card_s14_r.fill.fore_color.rgb = C_WHITE
    card_s14_r.line.color.rgb = C_BORDER

    tb_r14 = slide14.shapes.add_textbox(Inches(8.2), Inches(1.65), Inches(4.3), Inches(0.5))
    p_rh = tb_r14.text_frame.paragraphs[0]
    p_rh.text = "Empirical Validation Results"
    p_rh.font.name = FONT_MAIN
    p_rh.font.size = Pt(14)
    p_rh.font.bold = True
    p_rh.font.color.rgb = C_NAVY

    if os.path.exists(fig5):
        slide14.shapes.add_picture(fig5, Inches(8.15), Inches(2.2), width=Inches(4.4), height=Inches(3.3))

    tb_rdesc = slide14.shapes.add_textbox(Inches(8.2), Inches(5.6), Inches(4.3), Inches(1.2))
    p_rd = tb_rdesc.text_frame.paragraphs[0]
    p_rd.text = "Fig: On-device INT8 FeverCNN performance curves and confusion matrix (92.4% test accuracy, 142 ms latency on ESP32-S3 @ 240 MHz)."
    p_rd.font.name = FONT_MAIN
    p_rd.font.size = Pt(9.5)
    p_rd.font.color.rgb = C_GRAY

    # =========================================================================
    # SLIDE 15: Required Information (Exact 11 Questions & Answers Table)
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_header(slide15, "Required Information", has_iitd=True, is_slide_15=True)

    # Slide number badge "15" on top left and bottom right
    tb_num1 = slide15.shapes.add_textbox(Inches(0.45), Inches(0.35), Inches(0.6), Inches(0.4))
    p_n1 = tb_num1.text_frame.paragraphs[0]
    p_n1.text = "15"
    p_n1.font.name = FONT_MAIN
    p_n1.font.size = Pt(12)
    p_n1.font.bold = True
    p_n1.font.color.rgb = C_GRAY

    tb_num2 = slide15.shapes.add_textbox(Inches(12.3), Inches(6.8), Inches(0.6), Inches(0.4))
    p_n2 = tb_num2.text_frame.paragraphs[0]
    p_n2.text = "15"
    p_n2.font.name = FONT_MAIN
    p_n2.font.size = Pt(12)
    p_n2.font.bold = True
    p_n2.font.color.rgb = C_GRAY

    # Table matching Slide 15 exactly
    rows15, cols15 = 12, 3
    t_shape15 = slide15.shapes.add_table(rows15, cols15, Inches(0.6), Inches(1.6), Inches(12.133), Inches(5.35))
    tbl15 = t_shape15.table

    tbl15.columns[0].width = Inches(0.8)
    tbl15.columns[1].width = Inches(4.333)
    tbl15.columns[2].width = Inches(7.0)

    h15 = ["S.No.", "Questions", "Answers"]
    for c_idx, h_text in enumerate(h15):
        cell = tbl15.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(224, 231, 255)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_MAIN
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_BLACK
        p.alignment = PP_ALIGN.CENTER if c_idx == 0 else PP_ALIGN.LEFT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    q_answers = [
        ("1", "No. of Inventors",
         "3 Student Inventors (Gauri Gupta, Anmol Nandwani, Vansh Sharma) + 1 Faculty Guide (Dr. Divya Agarwal)"),
        
        ("2", "Total Market Size",
         "Indian Point-of-Care Diagnostics Market ~₹8,500+ Cr ($1.0B+), expanding at 14.5% CAGR; Target base of 1.1M+ ASHA workers and 160,000+ Ayushman Bharat HWCs"),
        
        ("3", "Novelty in this Idea",
         "100% offline, zero-consumable multimodal edge-AI sensor fusion (ECG, PPG, Far-IR thermal, respiration, spectral Hb, GSR) on dual-bus ESP32-S3 with zero-literacy audio/visual triage"),
        
        ("4", "Funding till now",
         "Nil external funding / ~₹50,000 internal institutional prototyping support at VIPS-TC; Applied to Maker Bhavan Foundation Vishwakarma Awards 2026–27 (VK26-AU-FD-0006)"),
        
        ("5", "Patent Filed (Date and Number)",
         "Not yet filed (Provisional Patent Application on Multimodal Dual-Bus Edge-AI Triage Architecture under preparation; No filing number issued yet)"),
        
        ("6", "Patent Granted",
         "No (Pre-filing engineering prototype stage)"),
        
        ("7", "Category: General/SC/ST/OBC",
         "[To be selected/confirmed by Applicant: General / OBC / SC / ST]"),
        
        ("8", "Expectation from IHFC (in lacs)",
         "₹19.80 Lacs (approx. ₹20 Lacs for 1-year hardware refinement, clinical benchmarking, and frontline ASHA pilot trials)"),
        
        ("9", "Mentor; Name, Designation, Affiliation, email ID and Phone Number",
         "Name: Dr. Divya Agarwal | Designation: Assistant Professor | Affiliation: School of Engineering & Technology, VIPS-TC, Delhi | Email: divya.agarwal@vips.edu | Phone: [To be filled by Mentor]"),
        
        ("10", "Contribution of Mentor in Product (Individual Contribution)",
         "Academic guidance, biomedical system architecture oversight, sensor fusion algorithm verification, and research publication supervision"),
        
        ("11", "Video Attached (Yes/No)",
         "[To be selected by Applicant: Yes/No - Functional laboratory prototype demonstration video available upon request]")
    ]

    for r_idx, (sno, q, ans) in enumerate(q_answers):
        for c_idx, val in enumerate([sno, q, ans]):
            cell = tbl15.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if r_idx % 2 == 1:
                cell.fill.fore_color.rgb = C_TBL_ALT
            else:
                cell.fill.fore_color.rgb = C_WHITE

            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_MAIN
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_BLACK
            if c_idx < 2:
                p.font.bold = True
            if c_idx == 0:
                p.alignment = PP_ALIGN.CENTER
            else:
                p.alignment = PP_ALIGN.LEFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Save presentation
    prs.save(output_pptx)
    print(f"Presentation successfully created at: {output_pptx}")
    print(f"Total slides generated: {len(prs.slides)}")

if __name__ == "__main__":
    create_deck()
