import zipfile
import xml.etree.ElementTree as ET

DOCX_IN = "Smart Asha Arogya AI updated paper (1).docx"

with zipfile.ZipFile(DOCX_IN, "r") as z:
    doc_xml = z.read("word/document.xml")

root = ET.fromstring(doc_xml)
ns = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}

paras = root.findall(".//w:p", ns)

for idx in [0, 20, 30, 113, 138, 170]:
    p = paras[idx]
    print(f"=== P{idx} ===")
    p_str = ET.tostring(p, encoding="utf-8").decode("utf-8")
    print(p_str[:300] + "...\n")
