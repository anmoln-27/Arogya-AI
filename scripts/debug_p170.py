import zipfile
import xml.etree.ElementTree as ET

DOCX1 = "Smart Asha Arogya AI updated paper (1).docx"
DOCX2 = "Smart Asha Arogya AI updated paper (corrected).docx"
ns = {"w": "http://purl.oclc.org/ooxml/wordprocessingml/main"}

with zipfile.ZipFile(DOCX1) as z1:
    r1 = ET.fromstring(z1.read("word/document.xml"))
with zipfile.ZipFile(DOCX2) as z2:
    r2 = ET.fromstring(z2.read("word/document.xml"))

ps1 = [("".join([t.text for t in p.findall(".//w:t", ns) if t.text])) for p in r1.findall(".//w:p", ns)]
ps2 = [("".join([t.text for t in p.findall(".//w:t", ns) if t.text])) for p in r2.findall(".//w:p", ns)]

print(f"Total ps1: {len(ps1)}, Total ps2: {len(ps2)}")
for i in range(len(ps1)):
    if ps1[i] != ps2[i]:
        t1 = ps1[i][:60].encode("ascii", errors="replace").decode("ascii")
        t2 = ps2[i][:60].encode("ascii", errors="replace").decode("ascii")
        print(f"Diff P{i}:\n  OLD: {t1}\n  NEW: {t2}")
