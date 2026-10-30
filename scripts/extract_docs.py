import pypdf
import os

out_path = r"C:\Users\Acer\.gemini\antigravity-ide\brain\daa4e2da-98d0-48b2-9b47-82babf201a05\scratch\extracted_docs.txt"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(out_path, "w", encoding="utf-8") as out:
    for path in [r"docs\Vishwakarma_Awards_2026_Proposal_Update.pdf", r"docs\Smart-ASHA Progress Report.pdf"]:
        if not os.path.exists(path):
            out.write(f"File not found: {path}\n")
            continue
        try:
            reader = pypdf.PdfReader(path)
            out.write(f"=== {path} ({len(reader.pages)} pages) ===\n")
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                out.write(f"--- Page {i+1} ---\n")
                out.write(text + "\n")
        except Exception as e:
            out.write(f"Error reading {path}: {e}\n")
print("Extraction complete.")
