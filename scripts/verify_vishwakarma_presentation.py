import re
import pptx
from pptx import Presentation

prs = Presentation('Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx')
print(f'Total slides: {len(prs.slides)}')

banned_words = ['Vidarbha', 'TerraWeed', 'weeder', r'\btine\b', r'\btines\b', 'COEP', 'cotton', 'soybean', 'glyphosate', 'tiller']
found_banned = []

required_terms = [
    'VK26-AU-FD-0006',
    'SMART-ASHA',
    'AD8232',
    'MAX30102',
    'MLX90640',
    'AS7343',
    'ESP32-S3',
    '92.4%',
    '8,950',
    'VIPS-TC'
]
found_terms = {t: False for t in required_terms}

for i, slide in enumerate(prs.slides):
    slide_text = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            slide_text.append(shape.text_frame.text)
        elif shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    slide_text.append(cell.text)
    full_slide_txt = ' '.join(slide_text)
    
    for bw in banned_words:
        if re.search(bw, full_slide_txt, re.IGNORECASE):
            found_banned.append((i+1, bw))
            
    for req in required_terms:
        if req.lower() in full_slide_txt.lower():
            found_terms[req] = True

print('--- VERIFICATION AUDIT RESULTS ---')
if found_banned:
    print(f'WARNING: Found residual template words: {found_banned}')
else:
    print('PASS: Zero residual exemplar agricultural words found across all 20 slides!')

print('\nRequired Terms Presence:')
all_pass = True
for term, present in found_terms.items():
    status = 'PASS' if present else 'FAIL'
    if not present:
        all_pass = False
    print(f'  [{status}] {term}: {present}')

if all_pass and not found_banned:
    print('\nOVERALL STATUS: 100% PERFECT VERIFICATION! ALL CHECKS PASSED!')
else:
    print('\nOVERALL STATUS: Some checks need review.')
