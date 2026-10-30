import pptx
from pptx import Presentation

prs = Presentation('Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx')

with open('docs/pptx_images_audit.txt', 'w', encoding='utf-8') as out:
    for idx, slide in enumerate(prs.slides):
        out.write(f'=== SLIDE {idx+1} ===\n')
        pic_count = 0
        for s_idx, shape in enumerate(slide.shapes):
            if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                pic_count += 1
                img = shape.image
                out.write(f'  Pic {pic_count} [Shape {s_idx}: {shape.name}]: pos=({shape.left}, {shape.top}), size=({shape.width} x {shape.height}), img_bytes={len(img.blob)}, ext={img.ext}\n')
        if pic_count == 0:
            out.write('  No pictures.\n')
print('Images audit written to docs/pptx_images_audit.txt')
