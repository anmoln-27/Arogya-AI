import os
import re
import subprocess
import markdown

md_path = r"docs\MCU_Architecture_Evaluation_ESP32S3_vs_STM32H533RE.md"
html_path = r"docs\MCU_Architecture_Evaluation_ESP32S3_vs_STM32H533RE.html"
pdf_path = r"docs\MCU_Architecture_Evaluation_ESP32S3_vs_STM32H533RE.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Pre-process callouts: > [!CAUTION] and > [!WARNING]
def replace_callout(match):
    kind = match.group(1).lower()
    content = match.group(2).strip()
    # Remove leading > from each line
    cleaned_lines = []
    for line in content.split("\n"):
        cleaned_lines.append(re.sub(r"^>\s?", "", line))
    inner_text = "\n".join(cleaned_lines)
    inner_html = markdown.markdown(inner_text, extensions=['tables', 'fenced_code'])
    badge_label = "CAUTION" if kind == "caution" else "WARNING" if kind == "warning" else "NOTE"
    return f"""<div class="callout callout-{kind}">
<div class="callout-header"><span class="badge badge-{kind}">{badge_label}</span></div>
<div class="callout-body">{inner_html}</div>
</div>"""

text = re.sub(r">\s*\[!(CAUTION|WARNING|NOTE|IMPORTANT)\]\s*\n((?:>.*(?:\n|$))*)", replace_callout, text)

# Replace mermaid diagram with an elegant HTML comparison card
mermaid_pattern = r"```mermaid[\s\S]*?```"
mermaid_replacement = """
<div class="pipeline-comparison">
    <div class="pipeline-card pipeline-esp">
        <div class="pipeline-title">ESP32-S3 Dual-Core Pipeline (Parallel)</div>
        <div class="pipeline-box"><strong>Core 0:</strong> Asynchronous AI Inference (110 ms) &rarr; Triage Output</div>
        <div class="pipeline-sep">|| (Concurrent Execution)</div>
        <div class="pipeline-box"><strong>Core 1:</strong> 400 kHz Optical Polling + ECG Filters + 60 FPS BLE &rarr; <strong>Mobile App (Zero Jitter)</strong></div>
        <div class="pipeline-badge success">Zero Optical Sample Loss</div>
    </div>
    <div class="pipeline-card pipeline-stm">
        <div class="pipeline-title">STM32H533RE Single-Core Pipeline (Time-Sliced)</div>
        <div class="pipeline-box"><strong>Single Cortex-M33 (250 MHz):</strong> Task 1: AI Inference (Active)</div>
        <div class="pipeline-sep">&darr; (Blocks CPU / Requires DMA)</div>
        <div class="pipeline-box"><strong>Shared Core:</strong> Task 2: Sensor Sampling &rarr; <strong>Risk of Sample Drops</strong></div>
        <div class="pipeline-badge danger">Requires Complex DMA Buffering</div>
    </div>
</div>
"""
text = re.sub(mermaid_pattern, mermaid_replacement, text)

# Clean up LaTeX formulas for clean presentation
# Display math
text = re.sub(r"\$\$\\text\{Core 0\} \\longrightarrow \\text\{Edge Impulse 2D-CNN Inference \(768-pixel thermopile array\)\}\$\$", 
              "<div class=\"math-block\"><strong>Core 0:</strong> Edge Impulse 2D-CNN Inference (768-pixel thermopile array)</div>", text)
text = re.sub(r"\$\$\\text\{Core 1\} \\longrightarrow \\text\{400 kHz Optical Polling \(MAX30105\), Digital Filtering \(SDNN/RMSSD\), OLED, BLE\}\$\$", 
              "<div class=\"math-block\"><strong>Core 1:</strong> 400 kHz Optical Polling (MAX30105), Digital Filtering (SDNN/RMSSD), OLED, BLE</div>", text)
text = re.sub(r"\$\$V = L \\cdot \\frac\{di\}\{dt\}\$\$", 
              "<div class=\"math-block\"><strong>Inductive Ground Bounce:</strong> <em>V = L &middot; (di / dt)</em></div>", text)

# Inline math cleanups
text = text.replace(r"$\sim 10.8\text{ bits}$", "~10.8 bits")
text = text.replace(r"$\sim 9.2\text{ bits}$", "~9.2 bits")
text = text.replace(r"$2.0\text{ A}$", "2.0 A")
text = text.replace(r"$80\text{ ms} - 140\text{ ms}$", "80 ms – 140 ms")
text = text.replace(r"$24 \times 32$", "24&times;32")
text = text.replace(r"$210 \times 125 \times 45\text{ mm}$", "210 &times; 125 &times; 45 mm")
text = text.replace(r"$70 \times 82 \times 18\text{ mm}$", "70 &times; 82 &times; 18 mm")
text = text.replace(r"$70 \times 82\text{ mm}$", "70 &times; 82 mm")
text = text.replace(r"$48 \times 38\text{ mm}$", "48 &times; 38 mm")
text = text.replace(r"$1000\,\mu\text{F}$", "1000 &mu;F")

# Convert markdown to HTML
html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart-ASHA | MCU Architecture Evaluation: ESP32-S3 vs STM32H533RE</title>
<style>
    @page {{
        size: A4;
        margin: 16mm 14mm 16mm 14mm;
        @bottom-right {{
            content: "Page " counter(page);
            font-size: 8.5pt;
            color: #718096;
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #1a202c;
        line-height: 1.5;
        font-size: 9.5pt;
        background: #ffffff;
        margin: 0;
        padding: 0;
    }}
    .header-banner {{
        background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 14px;
    }}
    .header-banner h1 {{
        color: #ffffff;
        font-size: 15pt;
        margin: 0 0 4px 0;
        border-bottom: none;
        padding-bottom: 0;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }}
    .header-banner .subtitle {{
        font-size: 10pt;
        color: #bee3f8;
        margin: 0 0 6px 0;
        font-weight: 500;
    }}
    .header-banner .meta-bar {{
        font-size: 8pt;
        color: #e2e8f0;
        border-top: 1px solid rgba(255,255,255,0.25);
        padding-top: 6px;
        margin-top: 6px;
    }}
    h1 {{
        font-size: 14pt;
        color: #1a365d;
        border-bottom: 2px solid #2b6cb0;
        padding-bottom: 4px;
        margin-top: 16px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }}
    h2 {{
        font-size: 11.5pt;
        color: #2b6cb0;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 3px;
        margin-top: 14px;
        margin-bottom: 6px;
    }}
    h3 {{
        font-size: 10pt;
        color: #2d3748;
        margin-top: 10px;
        margin-bottom: 4px;
        font-weight: 700;
    }}
    p {{
        margin-top: 0;
        margin-bottom: 6px;
        text-align: justify;
    }}
    strong {{
        color: #1a202c;
    }}
    ul, ol {{
        margin-top: 0;
        margin-bottom: 8px;
        padding-left: 18px;
    }}
    li {{
        margin-bottom: 3px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 8.2pt;
        page-break-inside: avoid;
    }}
    th, td {{
        border: 1px solid #cbd5e0;
        padding: 5px 7px;
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
        font-size: 8pt;
    }}
    pre {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #3182ce;
        padding: 6px 10px;
        border-radius: 4px;
        overflow-x: auto;
        margin: 8px 0;
        white-space: pre-wrap;
        word-break: break-word;
        page-break-inside: avoid;
    }}
    code {{
        background: #edf2f7;
        padding: 1px 4px;
        border-radius: 3px;
        color: #805ad5;
    }}
    .callout {{
        border-radius: 4px;
        padding: 8px 12px;
        margin: 10px 0;
        page-break-inside: avoid;
    }}
    .callout-caution {{
        background-color: #fffaf0;
        border: 1px solid #feebc8;
        border-left: 4px solid #dd6b20;
    }}
    .callout-warning {{
        background-color: #fff5f5;
        border: 1px solid #fed7d7;
        border-left: 4px solid #e53e3e;
    }}
    .callout-header {{
        margin-bottom: 4px;
    }}
    .badge {{
        display: inline-block;
        padding: 2px 7px;
        font-size: 7.5pt;
        font-weight: 700;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .badge-caution {{
        background-color: #dd6b20;
        color: white;
    }}
    .badge-warning {{
        background-color: #e53e3e;
        color: white;
    }}
    .pipeline-comparison {{
        display: flex;
        gap: 12px;
        margin: 10px 0;
        page-break-inside: avoid;
    }}
    .pipeline-card {{
        flex: 1;
        border: 1px solid #cbd5e0;
        border-radius: 5px;
        padding: 8px 10px;
        background: #ffffff;
    }}
    .pipeline-esp {{
        border-left: 4px solid #38a169;
        background: #f0fff4;
    }}
    .pipeline-stm {{
        border-left: 4px solid #e53e3e;
        background: #fff5f5;
    }}
    .pipeline-title {{
        font-weight: bold;
        font-size: 8.8pt;
        margin-bottom: 6px;
        color: #2d3748;
    }}
    .pipeline-box {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 8pt;
        margin: 4px 0;
    }}
    .pipeline-sep {{
        font-size: 7.5pt;
        color: #718096;
        text-align: center;
        margin: 2px 0;
        font-family: monospace;
    }}
    .pipeline-badge {{
        display: block;
        text-align: center;
        font-size: 7.5pt;
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 3px;
        margin-top: 6px;
    }}
    .pipeline-badge.success {{
        background: #c6f6d5;
        color: #22543d;
    }}
    .pipeline-badge.danger {{
        background: #fed7d7;
        color: #742a2a;
    }}
    .math-block {{
        background: #f7fafc;
        border-left: 3px solid #4299e1;
        padding: 5px 10px;
        font-size: 8.5pt;
        margin: 5px 0;
        font-family: "Consolas", monospace;
    }}
    hr {{
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 12px 0;
    }}
</style>
</head>
<body>
<div class="header-banner">
    <h1>Smart-ASHA (Arogya AI) &bull; Systems Architecture Analysis</h1>
    <div class="subtitle">Evaluating the Migration from ESP32-S3 to STM32H533RE (Nucleo-H533RE)</div>
    <div class="meta-bar">
        <strong>Application ID:</strong> VK26-AU-FD-0006 &bull; 
        <strong>Theme:</strong> Frontier Diagnostics: The Next Vital Signs &bull; 
        <strong>Author/Team:</strong> Gauri Gupta, Anmol Nandwani, Vansh Sharma (VIPS-TC)
    </div>
</div>
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

