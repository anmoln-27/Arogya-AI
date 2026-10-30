import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (corrected).docx"

with zipfile.ZipFile(DOCX, "r") as z:
    doc_xml = z.read("word/document.xml")
    footer_xml = z.read("word/footer1.xml")

root = ET.fromstring(doc_xml)
ns = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}

paragraphs = root.findall(".//w:p", ns)
tables = root.findall(".//w:tbl", ns)

p_texts = []
for p in paragraphs:
    texts = [t.text for t in p.findall(".//w:t", ns) if t.text]
    full_text = "".join(texts).strip()
    if full_text:
        p_texts.append(full_text)

full_doc_text = "\n".join(p_texts)

print("=" * 60)
print(f"VERIFICATION AUDIT OF: {DOCX}")
print("=" * 60)
print(f"Total Paragraphs with text: {len(p_texts)}")
print(f"Total Tables: {len(tables)}")
print()

checks = [
    ("C1 Title Updated", "Prototype for Preliminary Physiological Screening" in full_doc_text),
    ("C1 Title Exaggeration Removed", "Cardiopulmonary and Biochemical Triage Framework" not in full_doc_text),
    ("C1 Keywords Cleaned", "Edge AI, TinyML, ESP32-S3, sensor fusion" in full_doc_text),
    ("C2 Deep Scan Toned Down", "acquisition protocol designed to reduce transient" in full_doc_text),
    ("C2 Cost BOM Added (Rs 8,950)", "Rs 8,950" in full_doc_text),
    ("C3 Related Work Claims Toned Down", "greater measurement consistency" in full_doc_text),
    ("C4 Discussion Blood Claim Toned Down", "reduce the need for venepuncture during village visits" in full_doc_text),
    ("C4 SDG Claims Toned Down", "faster preliminary screening and triage-level flagging" in full_doc_text),
    ("C5 Thermal Detection Task Clarified", "classifying thermal frames as healthy versus elevated surface-temperature pattern" in full_doc_text),
    ("C8 Author Placeholders Removed", "[to be confirmed" not in full_doc_text),
    ("C8 Platform Hardware Specified", "7Semi ESP32-S3 EC200U 4G LTE Smart Modem" in full_doc_text),
    ("C8 Dual-Bus Architecture Specified", "Wire1 @ 400 kHz" in full_doc_text),
    ("C8 Sampling Rates Specified", "~67 Hz sampling rate" in full_doc_text),
    ("C9 Author Notes Removed", "This is a photograph of the physical prototype packaging" not in full_doc_text),
    ("C9 Reviewer Decal Note Removed", "the ECG module decal reads" not in full_doc_text),
    ("C10 Conclusion Toned Down", "deterministic, rule-based triage score" in full_doc_text),
    ("C12 Limitations Section Created", "VI. LIMITATIONS" in full_doc_text),
    ("C13 Deep Scan Signal List Expanded", "IMU-derived motion quality, and MQ-135 gas proxy" in full_doc_text),
    ("C15 British Spelling (artefacts)", "artefacts" in full_doc_text),
    ("C16 IEEE Footer Placeholder Removed", "XXX-X-XXXX-XXXX-X" not in footer_xml.decode("utf-8")),
    ("C17 Abstract Aligned (92.4%)", "92.4% classification accuracy on a held-out, subject-independent" in full_doc_text),
]

passed = 0
for label, cond in checks:
    status = "PASS" if cond else "FAIL"
    if cond:
        passed += 1
    print(f"[{status}] {label}")

print()
print("-" * 60)
print(f"Checklist Verification: {passed}/{len(checks)} checks passed!")
print("-" * 60)

# Check Tables
print("\nAuditing Tables:")
for ti, tbl in enumerate(tables):
    rows = tbl.findall(".//w:tr", ns)
    print(f"\n--- Table {ti} ({len(rows)} rows) ---")
    for ri, row in enumerate(rows):
        cells = row.findall(".//w:tc", ns)
        row_str = " | ".join(["".join([t.text for t in c.findall(".//w:t", ns) if t.text]).strip() for c in cells])
        print(f"  R{ri}: {row_str}".encode('ascii', errors='replace').decode('ascii'))

print("\nAudit Complete.")
