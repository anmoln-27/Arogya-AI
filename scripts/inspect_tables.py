import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1).docx"
ns = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}

with zipfile.ZipFile(DOCX) as z:
    root = ET.fromstring(z.read("word/document.xml"))

tables = root.findall(".//w:tbl", ns)
print(f"Total tables in original docx: {len(tables)}")
for i, tbl in enumerate(tables):
    rows = tbl.findall(".//w:tr", ns)
    print(f"\n--- Original Table {i} ({len(rows)} rows) ---")
    for ri, row in enumerate(rows):
        cells = row.findall(".//w:tc", ns)
        row_str = " | ".join(["".join([t.text for t in c.findall(".//w:t", ns) if t.text]).strip() for c in cells])
        print(f"  R{ri}: {row_str.encode('ascii', errors='replace').decode('ascii')}")
