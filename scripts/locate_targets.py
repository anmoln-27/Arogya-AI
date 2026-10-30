import os

OUT_DIR = r"C:\Users\Acer\.gemini\antigravity-ide\brain\08f9a3dd-6e1e-47c6-ac9d-2b7473ddf204\scratch"
with open(os.path.join(OUT_DIR, "docx_paragraphs.txt"), encoding="utf-8") as f:
    text = f.read()

paras = text.split("=== P")
print(f"Total paragraph blocks: {len(paras)}")

queries = [
    ("C1 Title", "Arogya AI: A Multi-Modal, Edge-AI Cardiopulmonary"),
    ("C1 Keywords", "Keywords—"),
    ("C2 Deep Scan", "A 60-second Deep Scan methodology"),
    ("C2 Cost", "A low-cost hardware prototype proving"),
    ("C3 Related Work 1", "multi-parameter healthcare screening systems generally display"),
    ("C3 Related Work 2", "develop a more effective diagnostic outcome"),
    ("C3 Related Work 3", "Arogya AI meets all four objectives"),
    ("C4 Discussion 1", "Having a non-invasive screening tool can indeed lessen reliance"),
    ("C4 Discussion 2", "It assists UN SDG 3"),
    ("C4 Discussion 3", "Arogya AI aids the reduction of inequalities"),
    ("C4 Discussion 4", "Low development cost with significantly reduced cost"),
    ("C5 Task alignment", "detection accuracy – 92.4% classifying"),
    ("C8 Platform identity", "[to be confirmed by the authors"),
    ("C8 Sampling rate", "[to be confirmed: per-sensor sampling rate"),
    ("C9 Author note", "This is a photograph of the physical prototype packaging"),
    ("C10 Conclusion 1", "with a reproducible, rule-based sensor-fusion score"),
    ("C10 Conclusion 2", "and achieves practical on-device inference latency"),
    ("C11 Future work TTS", "Cloud Text-to-Speech Pipeline with Multiple Languages"),
    ("C11 Future work Hb", "The current haemoglobin estimation channel requires manual"),
    ("C11 Future work Target", "the mass-market target identified in the feasibility study"),
    ("C13 Deep Scan signals", "collection of all multi-modal data signals (SpO"),
]

for label, q in queries:
    matches = []
    for p in paras[1:]:
        p_idx = p.split(" ")[0].strip()
        if q.lower() in p.lower():
            matches.append(p_idx)
    res = ", ".join(matches) if matches else "NOT FOUND"
    print(f"{label}: found in P{res}")
