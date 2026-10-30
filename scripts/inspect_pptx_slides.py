import pptx
from pptx import Presentation

prs = Presentation('Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx')
with open('docs/pptx_detailed_slides.txt', 'w', encoding='utf-8') as out:
    for idx, slide in enumerate(prs.slides):
        out.write(f'=== SLIDE {idx+1} ===\n')
        for s_idx, shape in enumerate(slide.shapes):
            if shape.has_text_frame:
                paragraphs = [p.text.strip() for p in shape.text_frame.paragraphs if p.text.strip()]
                if paragraphs:
                    out.write(f'  [Shape {s_idx}: {shape.name}] ({shape.left}, {shape.top}, {shape.width}, {shape.height}):\n')
                    for p in paragraphs:
                        out.write(f'    - {p}\n')
            elif shape.has_table:
                out.write(f'  [Table {s_idx}: {shape.name}] rows={len(shape.table.rows)}, cols={len(shape.table.columns)}\n')
                for r_idx, r in enumerate(shape.table.rows):
                    row_txt = [c.text.strip().replace('\n', ' ') for c in r.cells]
                    out.write(f'    Row {r_idx}: {" | ".join(row_txt)}\n')
            else:
                out.write(f'  [Other {s_idx}: {shape.name}] type={shape.shape_type}\n')
        out.write('\n')
print('Detailed inspection written to docs/pptx_detailed_slides.txt')
