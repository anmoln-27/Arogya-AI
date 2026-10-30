import os

files = [
    r'figures\Figure_6_Hardware_Prototype_Architecture.png',
    r'figures\cad_placeholder_slide7.png',
    r'figures\cad_placeholder_slide8.png',
    r'Smart Asha Arogya AI updated paper (corrected).docx',
    r'Smart Asha Arogya AI updated paper (1).docx',
    r'Arogya_AI_Manuscript_Revised.docx',
    r'Smart_ASHA_Vishwakarma_Stage_2_Submission.pptx',
    r'Vishwakarma Awards 2026-27 Stage 2 Submission Template.pptx',
    r'figures\Arogya_AI_Publication_Figures_and_Tables_Dossier.docx',
    r'hardware\assembly_guide.md',
    r'hardware\README.md',
    r'README.md',
    r'docs\Vishwakarma_Stage_2_PPT_Content.md',
    r'docs\Vishwakarma_Awards_2026_Proposal_Update.md',
    r'figures\README_FIGURES_AND_TABLES.md'
]

print(f"{'File':<62} | {'Size':<12} | {'Status'}")
print("-" * 84)
all_ok = True
for f in files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        size_str = f"{size:,} B"
        print(f"{f:<62} | {size_str:<12} | OK")
    else:
        print(f"{f:<62} | {'MISSING':<12} | FAIL")
        all_ok = False

if all_ok:
    print("\nALL 15 TARGET FILES VERIFIED SUCCESSFULLY!")
