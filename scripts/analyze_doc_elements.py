import os
import zipfile
import xml.etree.ElementTree as ET

DOCX_IN = "Smart Asha Arogya AI updated paper (1).docx"
OUT_DIR = r"C:\Users\Acer\.gemini\antigravity-ide\brain\08f9a3dd-6e1e-47c6-ac9d-2b7473ddf204\scratch"
os.makedirs(OUT_DIR, exist_ok=True)

with zipfile.ZipFile(DOCX_IN, "r") as z:
    doc_xml = z.read("word/document.xml")

root = ET.fromstring(doc_xml)
ns = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}

# Dump all paragraphs with text and their runs
with open(os.path.join(OUT_DIR, "docx_paragraphs.txt"), "w", encoding="utf-8") as out:
    for i, p in enumerate(root.findall(".//w:p", ns)):
        texts = [t.text for t in p.findall(".//w:t", ns) if t.text]
        full_text = "".join(texts).strip()
        if full_text:
            out.write(f"=== P{i} ===\n{full_text}\n\n")

print("Dumped paragraphs to scratch/docx_paragraphs.txt")

# Also dump tables
with open(os.path.join(OUT_DIR, "docx_tables.txt"), "w", encoding="utf-8") as out:
    for ti, tbl in enumerate(root.findall(".//w:tbl", ns)):
        out.write(f"=== Table {ti} ===\n")
        for ri, row in enumerate(tbl.findall(".//w:tr", ns)):
            row_cells = []
            for ci, cell in enumerate(row.findall(".//w:tc", ns)):
                cell_text = "".join([t.text for t in cell.findall(".//w:t", ns) if t.text]).strip()
                row_cells.append(cell_text)
            out.write(f"R{ri}: {' | '.join(row_cells)}\n")
        out.write("\n")

print("Dumped tables to scratch/docx_tables.txt")
