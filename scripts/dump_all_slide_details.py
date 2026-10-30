import pptx
from pptx import Presentation

prs = Presentation('Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx')

with open('docs/all_slide_details_utf8.txt', 'w', encoding='utf-8') as out:
    for i, slide in enumerate(prs.slides):
        out.write(f'============================== SLIDE {i+1} ==============================\n')
        for s_idx, shape in enumerate(slide.shapes):
            if shape.has_text_frame:
                full_txt = '\n'.join([p.text for p in shape.text_frame.paragraphs if p.text.strip()])
                if full_txt:
                    out.write(f'Shape {s_idx} [{shape.name}] (left={shape.left}, top={shape.top}, w={shape.width}, h={shape.height}):\n')
                    for line in full_txt.split('\n')[:6]:
                        out.write(f'   | {line}\n')
            elif shape.has_table:
                t = shape.table
                rows = list(t.rows)
                out.write(f'Table {s_idx} [{shape.name}] ({len(rows)}x{len(t.columns)}) (left={shape.left}, top={shape.top}):\n')
                for r in rows[:6]:
                    row_str = ' | '.join([c.text.strip().replace('\n', ' ') for c in r.cells])
                    out.write(f'   | {row_str}\n')
            elif shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                if shape.width > 2000000 and shape.height > 1500000 and shape.left > 100000:
                    out.write(f'CONTENT PICTURE {s_idx} [{shape.name}] (left={shape.left}, top={shape.top}, w={shape.width}, h={shape.height})\n')
print('UTF-8 dump written to docs/all_slide_details_utf8.txt')
