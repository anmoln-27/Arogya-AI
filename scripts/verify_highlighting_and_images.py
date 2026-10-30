import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1).docx"
NS = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}

with zipfile.ZipFile(DOCX) as z:
    doc_xml = z.read("word/document.xml")

root = ET.fromstring(doc_xml)

print("=" * 60)
print(f"VERIFYING DOCUMENT: {DOCX}")
print("=" * 60)

# 1. Verify Yellow Highlighting
highlight_elements = root.findall(".//w:highlight", NS)
print(f"Total <w:highlight> tags found: {len(highlight_elements)}")
yellow_highlights = [h for h in highlight_elements if h.attrib.get(f"{{{NS['w']}}}val") == "yellow"]
print(f"Yellow highlight tags: {len(yellow_highlights)}")
assert len(yellow_highlights) > 0, "No yellow highlights found!"

# Check specific key sections for highlighting
key_checks = [
    ("Title", lambda p: "Arogya AI: A Multi-Modal, Edge-AI Prototype" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Abstract", lambda p: "Abstract— In India" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Keywords", lambda p: "Keywords— Edge AI" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Roadmap", lambda p: "Section IV presents experimental bench results" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section III-D (AD8232)", lambda p: "AD8232 Single-Lead ECG" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section III-G (Sensor Fusion)", lambda p: "Sensor Fusion Architecture and Triage Engine" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section III-I (Ethics Statement)", lambda p: "Ethics and Informed Consent Statement" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section IV-B P170", lambda p: "The full inference path" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section VI (Limitations)", lambda p: "VI. LIMITATIONS" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section VII (Conclusion)", lambda p: "Arogya AI demonstrates the engineering feasibility" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Section VIII (Future Work)", lambda p: "VIII. FUTURE WORK" in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
    ("Reference [22]", lambda p: '[22] Analog Devices, "AD8232:' in "".join([t.text for t in p.findall(".//w:t", NS) if t.text])),
]

print("\n--- Key Section Highlighting Checks ---")
all_paragraphs = root.findall(".//w:p", NS)
for name, check_fn in key_checks:
    found = False
    is_hl = False
    for p in all_paragraphs:
        if check_fn(p):
            found = True
            hl = p.findall(".//w:highlight", NS)
            if any(h.attrib.get(f"{{{NS['w']}}}val") == "yellow" for h in hl):
                is_hl = True
            break
    print(f"[{'PASS' if is_hl else 'FAIL'}] {name}: found={found}, yellow_highlighted={is_hl}")
    assert is_hl, f"Failed yellow highlight check for {name}"

# Check Table III highlighting
tables = root.findall(".//w:tbl", NS)
t3 = tables[2] # Table III
t3_hl = t3.findall(".//w:highlight", NS)
print(f"[{'PASS' if len(t3_hl) > 0 else 'FAIL'}] Table III: {len(t3_hl)} yellow highlight tags")
assert len(t3_hl) > 0, "Table III lacks yellow highlights"

# 2. Verify Drawings Formatting & Dimensions
print("\n--- DrawingML Formatting & Dimensions Checks ---")
drawings = root.findall(".//w:drawing", NS)
print(f"Total drawings found: {len(drawings)}")
assert len(drawings) == 7, f"Expected 7 drawings, found {len(drawings)}"

for i, d in enumerate(drawings):
    extents = []
    for elem in d.iter():
        if elem.tag.endswith("extent") or elem.tag.endswith("ext"):
            cx = elem.attrib.get("cx")
            cy = elem.attrib.get("cy")
            if cx and cy:
                extents.append((int(cx), int(cy)))
                
    assert len(extents) >= 2, f"Drawing {i} missing extent tags"
    cx, cy = extents[0]
    aspect = cx / cy
    
    # Check parent paragraph
    parent_p = None
    for p in all_paragraphs:
        if d in list(p.iter()):
            parent_p = p
            break
            
    assert parent_p is not None, f"Drawing {i} parent paragraph not found"
    pPr = parent_p.find(f"{{{NS['w']}}}pPr")
    jc = pPr.find(f"{{{NS['w']}}}jc").attrib.get(f"{{{NS['w']}}}val") if pPr is not None and pPr.find(f"{{{NS['w']}}}jc") is not None else None
    ind = pPr.find(f"{{{NS['w']}}}ind")
    firstLine = ind.attrib.get(f"{{{NS['w']}}}firstLine") if ind is not None else None
    left_ind = ind.attrib.get(f"{{{NS['w']}}}left") if ind is not None else None
    
    print(f"Drawing {i}: cx={cx} ({cx/914400:.2f} in), cy={cy} ({cy/914400:.2f} in), aspect={aspect:.3f}, jc={jc}, firstLine={firstLine}, left={left_ind}")
    assert jc == "center", f"Drawing {i} is not center-aligned (jc={jc})"
    assert firstLine in [None, "0"], f"Drawing {i} has non-zero firstLine indent ({firstLine})"
    assert left_ind in [None, "0"], f"Drawing {i} has non-zero left indent ({left_ind})"

print("\n" + "=" * 60)
print("ALL VERIFICATIONS PASSED WITH 100% SUCCESS!")
print("=" * 60)
