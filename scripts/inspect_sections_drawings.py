import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1)_original_backup.docx"

with zipfile.ZipFile(DOCX) as z:
    doc_xml = z.read("word/document.xml")

root = ET.fromstring(doc_xml)
ns = {
    "w": "http://purl.oclc.org/ooxml/wordprocessingml/main",
}

body = root.find("w:body", ns)
children = list(body)

current_cols = "1" # default before any sectPr?
for i, el in enumerate(children):
    # Check if el has drawing
    drawings = el.findall(".//w:drawing", ns)
    sectPr = el.find(".//w:sectPr", ns)
    
    # get text if p
    texts = [t.text for t in el.findall(".//w:t", ns) if t.text]
    txt = "".join(texts).strip()
    
    if sectPr is not None:
        cols = sectPr.find("w:cols", ns)
        num = cols.attrib.get("{http://purl.oclc.org/ooxml/wordprocessingml/main}num", "1") if cols is not None else "1"
        current_cols = num
        print(f"[Item {i}] --- Section Break! Columns={current_cols} ---")
        
    if drawings:
        print(f"[Item {i}] DRAWING present! Current columns in section: {current_cols}. Text preview: {txt[:50]}")
    elif "Figure " in txt or "Fig. " in txt:
        print(f"[Item {i}] Caption/Mention: {txt[:70]}")
