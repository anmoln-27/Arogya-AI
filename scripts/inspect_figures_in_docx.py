import zipfile
import xml.etree.ElementTree as ET

DOCX = "Smart Asha Arogya AI updated paper (1).docx"

with zipfile.ZipFile(DOCX, "r") as z:
    media = [n for n in z.namelist() if "media/" in n]
    print(f"Total media files in docx: {len(media)}")
    for m in media:
        data = z.read(m)
        print(f"  {m}: {len(data)} bytes")
        
    rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8")
    root_rels = ET.fromstring(rels_xml)
    print("\nImage relationships:")
    for rel in root_rels:
        r_id = rel.attrib.get("Id")
        r_target = rel.attrib.get("Target")
        r_type = rel.attrib.get("Type")
        if "image" in r_type.lower():
            print(f"  Id: {r_id} -> Target: {r_target}")
            
    doc_xml = z.read("word/document.xml")
    root_doc = ET.fromstring(doc_xml)
    ns = {
        "w": "http://purl.oclc.org/ooxml/wordprocessingml/main",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/relationships",
        "blip": "http://schemas.openxmlformats.org/drawingml/2006/main"
    }
    
    # Search for all blip r:embed
    drawings = root_doc.findall(".//a:blip", {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"})
    print(f"\nTotal blip elements with schemas.openxmlformats.org: {len(drawings)}")
    # Also check with purl.oclc.org
    drawings_purl = root_doc.findall(".//{http://purl.oclc.org/ooxml/drawingml/main}blip")
    print(f"Total blip elements with purl: {len(drawings_purl)}")
    for d in drawings_purl:
        print("  Blip attribs:", d.attrib)
