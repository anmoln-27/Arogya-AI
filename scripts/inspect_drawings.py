import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1)_original_backup.docx"

with zipfile.ZipFile(DOCX) as z:
    doc_xml = z.read("word/document.xml")
    rels_xml = z.read("word/_rels/document.xml.rels")

root = ET.fromstring(doc_xml)
rels_root = ET.fromstring(rels_xml)

# Map rId to target image
rid_map = {}
for r in rels_root.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
    rid_map[r.attrib["Id"]] = r.attrib["Target"]

ns = {
    "w": "http://purl.oclc.org/ooxml/wordprocessingml/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

drawings = root.findall(".//w:drawing", ns)
print(f"Total drawings found: {len(drawings)}")

for i, d in enumerate(drawings):
    # Find blip
    blip = d.find(".//a:blip", ns)
    embed_id = blip.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed") if blip is not None else None
    target_img = rid_map.get(embed_id, "unknown")
    
    # Extents
    extent = d.find(".//wp:extent", ns)
    cx = extent.attrib.get("cx") if extent is not None else None
    cy = extent.attrib.get("cy") if extent is not None else None
    
    # Parent paragraph
    # Let's find parent paragraph of d
    parent_p = None
    for p in root.findall(".//w:p", ns):
        if d in p.findall(".//w:drawing", ns):
            parent_p = p
            break
            
    pPr_info = ""
    if parent_p is not None:
        pPr = parent_p.find("w:pPr", ns)
        if pPr is not None:
            spacing = pPr.find("w:spacing", ns)
            sp_info = spacing.attrib if spacing is not None else "no spacing"
            jc = pPr.find("w:jc", ns)
            jc_val = jc.attrib.get("{http://purl.oclc.org/ooxml/wordprocessingml/main}val") if jc is not None else "no jc"
            pPr_info = f"jc: {jc_val}, spacing: {sp_info}"
            
    print(f"\nDrawing {i}: Target={target_img}, EmbedID={embed_id}")
    print(f"  Extent: cx={cx} ({int(cx)/914400:.2f} in), cy={cy} ({int(cy)/914400:.2f} in)")
    print(f"  Parent pPr: {pPr_info}")
