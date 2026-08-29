# 📂 Scripts — Training & Data Pipelines

This directory contains the **executable Python scripts** for data processing, model training, and model export.

> **Run all scripts from the project root**, not from within this directory.

## Script Reference

### 🧠 Model Training

| Script | Description | Usage |
|:-------|:------------|:------|
| `train_fever_model.py` | Train the FeverCNN on thermal data | `python scripts/train_fever_model.py` |
| `fever_forehead_cnn.py` | Experimental CNN with forehead ROI focus | `python scripts/fever_forehead_cnn.py` |

### 📦 Model Export

| Script | Description | Usage |
|:-------|:------------|:------|
| `export_fever_to_onnx.py` | Export trained PyTorch model to ONNX | `python scripts/export_fever_to_onnx.py` |
| `finalize_onnx.py` | Finalize ONNX model (shape inference, optimization) | `python scripts/finalize_onnx.py` |
| `integrate_onnx_weights.py` | Integrate external weights into ONNX graph | `python scripts/integrate_onnx_weights.py` |

### 📊 Data Processing

| Script | Description | Usage |
|:-------|:------------|:------|
| `augment_fever_data.py` | Augment thermal data (noise, rotation, flip) | `python scripts/augment_fever_data.py` |
| `auto_collect.py` | Automated data collection from serial port | `python scripts/auto_collect.py` |
| `combine_all_thermal_data.py` | Merge multiple thermal data sources | `python scripts/combine_all_thermal_data.py` |
| `reach_target_dataset.py` | Grow dataset to target sample count | `python scripts/reach_target_dataset.py` |
| `split_dataset.py` | Split data into train/val/test sets | `python scripts/split_dataset.py` |
| `format_for_edge_impulse.py` | Format data for Edge Impulse upload | `python scripts/format_for_edge_impulse.py` |

### 📈 Visualization

| Script | Description | Usage |
|:-------|:------------|:------|
| `generate_visualizations.py` | Generate training curves, metrics, and comparison plots | `python scripts/generate_visualizations.py` |

## Typical Workflow

```bash
# 1. Collect data from ESP32
python utils/asha_logger.py

# 2. Clean and prepare
python utils/clean_dataset.py

# 3. Augment
python scripts/augment_fever_data.py

# 4. Train
python scripts/train_fever_model.py

# 5. Export
python scripts/export_fever_to_onnx.py
python scripts/finalize_onnx.py

# 6. Verify
python tests/verify_test_samples.py

# 7. Visualize
python scripts/generate_visualizations.py
```
