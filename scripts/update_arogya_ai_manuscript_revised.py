"""
Update Arogya_AI_Manuscript_Revised.docx with:
1. High-res Figure 6 composite (CAD isometric, orthographic views, and physical prototype)
2. Updated Drawing dimensions (6.5 in width, preserved aspect ratio)
3. Updated Figure 6 caption and explanatory note
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image

DOCX_PATH = "Arogya_AI_Manuscript_Revised.docx"
FIG6_PATH = r"figures\Figure_6_Hardware_Prototype_Architecture.png"

with Image.open(FIG6_PATH) as im:
    w_px, h_px = im.size

cx = 5943600 # 6.50 inches
cy = int(round(cx * h_px / w_px))

with zipfile.ZipFile(DOCX_PATH, "r") as zin:
    all_entries = {n: zin.read(n) for n in zin.namelist()}

doc_xml = all_entries["word/document.xml"].decode("utf-8")
root = ET.fromstring(doc_xml.encode("utf-8"))

ns = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
}

# Update extent on drawing containing rId14 (image6.png)
for d in root.findall(".//w:drawing", ns):
    blip = d.find(".//a:blip", ns)
    if blip is not None:
        embed = blip.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        if embed == "rId14":
            extent = d.find(".//wp:extent", ns)
            if extent is not None:
                extent.attrib["cx"] = str(cx)
                extent.attrib["cy"] = str(cy)
                print(f"Updated Drawing extent: cx={cx}, cy={cy}")

# Update caption paragraph (P105) and note (P106)
for p in root.findall(".//w:p", ns):
    t_nodes = p.findall(".//w:t", ns)
    p_text = "".join([t.text for t in t_nodes if t.text])
    if "Figure 6. Proposed Prototype" in p_text:
        # replace with comprehensive caption
        new_caption = (
            "Fig. 6. Arogya AI frontline screening workstation: (a) 3D isometric CAD rendering of ergonomic handheld enclosure "
            "(medical-grade ASA polymer, 210 × 125 × 45 mm, <450 g) with integrated carry handle, 128×64 OLED display window, tactile controls, and lateral sensor jacks; "
            "(b) Multi-view first-angle orthographic CAD drawings (Drawings 2–7 of Indian Patent Design Registration IDF) covering front elevation, top plan view, "
            "left biosensor inputs (Lead-I ECG, SpO2, GSR), right I/O & charging interfaces (USB-C, HDMI, RJ45, DC power), rear ventilation grille and battery service bay, "
            "and bottom anti-skid silicone feet; (c) Fabricated physical hardware prototype bench kit (smart_box_box.jpeg) validated in on-device testing with healthy volunteers."
        )
        if t_nodes:
            t_nodes[0].text = new_caption
            for tn in t_nodes[1:]:
                tn.text = ""
        print("Updated Figure 6 caption in Arogya_AI_Manuscript_Revised.docx")
        
    elif "Note: This is a photograph of the physical prototype packaging" in p_text:
        new_note = (
            "Note: Panels (a) and (b) present the 3D CAD ergonomic enclosure model and first-angle projection orthographic engineering views registered under "
            "the Indian Patent Design search / Idea Disclosure Form (IDF). Panel (c) illustrates the physical bench prototype packaging and sensor apertures "
            "fabricated for volunteer testing."
        )
        if t_nodes:
            t_nodes[0].text = new_note
            for tn in t_nodes[1:]:
                tn.text = ""
        print("Updated Figure 6 explanatory note in Arogya_AI_Manuscript_Revised.docx")

# Repackage docx
with open(FIG6_PATH, "rb") as f_img:
    fig6_bytes = f_img.read()

all_entries["word/document.xml"] = ET.tostring(root, encoding="utf-8")
all_entries["word/media/image6.png"] = fig6_bytes

with zipfile.ZipFile(DOCX_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zout:
    for fname, data in all_entries.items():
        zout.writestr(fname, data)

print(f"Successfully updated {DOCX_PATH} ({os.path.getsize(DOCX_PATH)} bytes)")
