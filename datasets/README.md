# 📂 Datasets — Curated ML-Ready Data

This directory contains **processed, labeled datasets** ready for machine learning model training and evaluation.

## Datasets

| Directory | Type | Purpose | Format |
|:----------|:-----|:--------|:-------|
| `SmartASHA_Dataset/` | Thermal Images | Primary fever/healthy classification dataset | 24×32 `.npy` arrays |
| `SmartASHA_Test_Images/` | Thermal PNGs | Visual verification and qualitative testing | `.png` images |
| `SmartASHA_Test_Samples/` | Thermal Arrays | Automated model verification | `.npy` arrays |
| `Arogya AI_Multimodal_Dataset/` | Multimodal CSV | Combined ECG, GSR, Gas, PPG, Temp data | `.csv` files |
| `Arogya AI_EdgeImpulse/` | Edge Impulse Format | Formatted for Edge Impulse BYOM upload | `.csv` with headers |
| `edge_impulse_format/` | Edge Impulse Export | Alternative Edge Impulse formatted data | `.csv` files |

## Dataset Preparation

### From Raw Data → Training Dataset

```bash
# 1. Clean raw data
python utils/clean_dataset.py

# 2. Augment fever data (add diversity)
python scripts/augment_fever_data.py

# 3. Split into train/val/test
python scripts/split_dataset.py

# 4. Format for Edge Impulse (optional)
python scripts/format_for_edge_impulse.py
```

## Thermal Image Format

- **Resolution**: 24 × 32 pixels (768 values)
- **Data Type**: float32 (temperature in °C)
- **Classes**: `fever/` and `healthy/`
- **Normalization**: Min-max normalized to [0, 1] range
