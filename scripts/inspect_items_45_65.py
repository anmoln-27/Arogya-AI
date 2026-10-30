import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1)_original_backup.docx"

with zipfile.ZipFile(DOCX) as z:
    root = ET.fromstring(z.read("word/document.xml"))

ns = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}
children = list(root.find("w:body", ns))

for i in range(45, 65):
    c = children[i]
    tag = c.tag.split("}")[-1]
    txt = "".join([t.text for t in c.findall(".//w:t", ns) if t.text]).strip()
    has_drawing = len(c.findall(".//w:drawing", ns)) > 0
    has_sectPr = len(c.findall(".//w:sectPr", ns)) > 0
    sect_info = ""
    if has_sectPr:
        s = c.find(".//w:sectPr", ns)
        cols = s.find("w:cols", ns)
        num = cols.attrib.get(f"{{{ns['w']}}}num", "1") if cols is not None else "1"
        sect_info = f" [SectPr: cols={num}]"
    print(f"Item {i}: tag={tag}, drawing={has_drawing}{sect_info}, text={txt[:75].encode('ascii', errors='replace').decode('ascii')}")
