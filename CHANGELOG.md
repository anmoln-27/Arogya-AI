# Changelog

All notable changes to the **Arogya AI** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.0] — 2026-08-29

### Added
- **Arogya AI_2.0_inferencing** — Edge Impulse v2.0 inference library with multi-board support (ESP32, Arduino Nano 33 BLE, Portenta H7, Nicla Vision, RP2040, Sony Spresense)
- Multimodal sensor data pipeline (ECG, GSR, Gas, PPG, Thermal)
- Spectral data parsing for anemia detection (`parse_spectral_data.py`)
- Comprehensive project documentation and architecture guide
- Professional repository structure with per-directory README files
- `.gitignore`, `.gitattributes` (LFS), `CONTRIBUTING.md`, `requirements.txt`

### Changed
- Repository reorganized into clean modular structure
- Edge Impulse libraries moved to dedicated `edge-impulse/` directory
- README completely rewritten with badges, architecture diagrams, and quick-start guide

---

## [1.0.0] — 2026-04-22

### Added
- **FeverCNN** model — custom CNN for fever detection from 24×32 thermal images
- PyTorch training pipeline (`train_fever_model.py`)
- ONNX export pipeline (`export_fever_to_onnx.py`)
- **Arogya AI_Inference** — Edge Impulse v1.0 C++ inference library
- Serial data logger (`asha_logger.py`) for real-time sensor data collection
- Data augmentation pipeline (`augment_fever_data.py`)
- Test sample generation and verification scripts
- Visualization generation (training curves, model metrics, thermal comparisons)
- SmartASHA_Dataset with labeled thermal images (Fever/Healthy)
- Project report and practicum presentation

### Model Results
- Fever Detection Accuracy: **100%** (Confidence: 99.27%)
- Healthy Detection Accuracy: **100%** (Confidence: 98.01%)
- Model Size: **~119 KB** (ONNX)
