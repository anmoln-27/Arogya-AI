import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1)_original_backup.docx"

with zipfile.ZipFile(DOCX) as z:
    doc_xml = z.read("word/document.xml")
    rels_xml = z.read("word/_rels/document.xml.rels")

root = ET.fromstring(doc_xml)
rels_root = ET.fromstring(rels_xml)

rid_map = {}
for r in rels_root.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
    rid_map[r.attrib["Id"]] = r.attrib["Target"]

# Register all possible namespaces or search by local tag
drawings = []
for elem in root.iter():
    if elem.tag.endswith("drawing"):
        drawings.append(elem)

print(f"Total drawings found: {len(drawings)}")

for i, d in enumerate(drawings):
    # find blip
    embed_id = None
    for b in d.iter():
        if b.tag.endswith("blip"):
            embed_id = b.attrib.get("{http://purl.oclc.org/ooxml/officeDocument/relationships}embed")
            if not embed_id:
                embed_id = b.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
    
    # extent
    cx, cy = None, None
    for ext in d.iter():
        if ext.tag.endswith("extent"):
            cx = ext.attrib.get("cx")
            cy = ext.attrib.get("cy")
            break
            
    target = rid_map.get(embed_id, "unknown")
    cx_in = float(cx)/914400 if cx else 0
    cy_in = float(cy)/914400 if cy else 0
    aspect = (cx_in / cy_in) if cy_in else 0
    print(f"Drawing {i}: Target={target}, Embed={embed_id}")
    print(f"  Dimensions: cx={cx} ({cx_in:.2f} in), cy={cy} ({cy_in:.2f} in), Aspect={aspect:.3f}")
