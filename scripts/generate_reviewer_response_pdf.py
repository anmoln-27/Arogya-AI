import os
import markdown
import subprocess

md_path = r"docs\Response_to_Reviewer_Comments_Vishwakarma_2026.md"
html_path = r"docs\Response_to_Reviewer_Comments_Vishwakarma_2026.html"
pdf_path = r"docs\Response_to_Reviewer_Comments_Vishwakarma_2026.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Convert markdown to HTML
html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Response to Reviewer Comments | Vishwakarma Awards 2026-27 | VK26-AU-FD-0006</title>
<style>
    @page {{
        size: A4;
        margin: 18mm 16mm 18mm 16mm;
        @bottom-right {{
            content: "Page " counter(page);
            font-size: 9pt;
            color: #718096;
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #1a202c;
        line-height: 1.55;
        font-size: 10pt;
        background: #ffffff;
        margin: 0;
        padding: 0;
    }}
    h1 {{
        font-size: 16pt;
        color: #1a365d;
        border-bottom: 2.5px solid #2b6cb0;
        padding-bottom: 6px;
        margin-top: 0;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    h2 {{
        font-size: 12pt;
        color: #2b6cb0;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
        margin-top: 14px;
        margin-bottom: 8px;
    }}
    h3 {{
        font-size: 10.8pt;
        color: #2d3748;
        margin-top: 14px;
        margin-bottom: 6px;
    }}
    h4 {{
        font-size: 10pt;
        color: #4a5568;
        margin-top: 10px;
        margin-bottom: 4px;
    }}
    h5 {{
        font-size: 9.5pt;
        color: #2b6cb0;
        margin-top: 8px;
        margin-bottom: 4px;
        text-transform: uppercase;
    }}
    p {{
        margin-top: 0;
        margin-bottom: 8px;
        text-align: justify;
    }}
    strong {{
        color: #1a202c;
    }}
    ul, ol {{
        margin-top: 0;
        margin-bottom: 10px;
        padding-left: 20px;
    }}
    li {{
        margin-bottom: 4px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 8.5pt;
        page-break-inside: avoid;
    }}
    th, td {{
        border: 1px solid #cbd5e0;
        padding: 6px 8px;
        text-align: left;
        vertical-align: top;
    }}
    th {{
        background-color: #ebf8ff;
        color: #2b6cb0;
        font-weight: 600;
    }}
    tr:nth-child(even) {{
        background-color: #f7fafc;
    }}
    pre, code {{
        font-family: "Consolas", "Courier New", monospace;
        font-size: 8.2pt;
    }}
    pre {{
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #3182ce;
        padding: 8px 12px;
        border-radius: 4px;
        overflow-x: auto;
        margin: 10px 0;
        white-space: pre-wrap;
        word-break: break-word;
    }}
    code {{
        background: #edf2f7;
        padding: 1px 4px;
        border-radius: 3px;
        color: #805ad5;
    }}
    blockquote {{
        margin: 8px 0;
        padding: 6px 14px;
        background-color: #f0f4f8;
        border-left: 4px solid #3182ce;
        font-style: italic;
        color: #2d3748;
    }}
    hr {{
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 14px 0;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"HTML written to {html_path}")

# Run Edge headless to print to PDF
edge_cmd = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={os.path.abspath(pdf_path)}",
    f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
]

print("Rendering PDF with Microsoft Edge headless...")
result = subprocess.run(edge_cmd, capture_output=True, text=True)
print("PDF Render Result Code:", result.returncode)
if os.path.exists(pdf_path):
    print(f"SUCCESS: PDF created at {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
else:
    print("PDF generation failed.")
