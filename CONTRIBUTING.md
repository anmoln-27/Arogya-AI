# Contributing to Arogya AI

Thank you for your interest in contributing to **Arogya AI**! 🩺

This guide will help you get started with contributing to our project.

---

## 🚀 Getting Started

### 1. Fork the Repository

Click the **Fork** button at the top-right corner of the [Arogya AI repo](https://github.com/anmoln-27/Arogya AI).

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/Arogya AI.git
cd Arogya AI
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📝 Branch Naming Convention

| Branch Type | Format | Example |
|:------------|:-------|:--------|
| Feature | `feature/<description>` | `feature/add-spo2-model` |
| Bug Fix | `fix/<description>` | `fix/thermal-calibration` |
| Documentation | `docs/<description>` | `docs/update-hardware-bom` |
| Experiment | `experiment/<description>` | `experiment/resnet-fever` |

---

## 🧪 Before Submitting

- [ ] Run existing tests: `python tests/verify_test_samples.py`
- [ ] Ensure code follows the existing style (PEP 8 for Python)
- [ ] Update documentation if you've changed interfaces
- [ ] Add docstrings to new functions/classes
- [ ] Keep model files under `models/` and data under `data/` or `datasets/`

---

## 📬 Pull Request Process

1. Push your branch to your fork
2. Open a Pull Request against the `main` branch
3. Provide a clear description of your changes
4. Reference any related issues
5. Wait for review from a team member

---

## 📂 Project Structure Rules

- **Scripts** go in `scripts/` — executable pipelines for training, export, data processing
- **Utilities** go in `utils/` — shared helpers, config, model definitions
- **Tests** go in `tests/` — verification and validation scripts
- **Data** goes in `data/` — raw sensor logs (CSV, NPY)
- **Datasets** go in `datasets/` — curated, ML-ready datasets
- **Models** go in `models/` — trained weights (.pth, .onnx)
- **Edge Impulse** libraries go in `edge-impulse/` — C++ inference SDKs
- **Documentation** goes in `docs/` — reports, presentations, architecture docs

---

## 🔧 Hardware Contributions

If you're contributing hardware-related changes:

- Update the BOM in `hardware/README.md`
- Include wiring diagrams or schematics as images
- Document pin connections and power requirements
- Test on actual ESP32-S3 hardware before submitting

---

## 💬 Questions?

Open an [Issue](https://github.com/anmoln-27/Arogya AI/issues) or reach out to the team.

---

**Thank you for helping make healthcare accessible! ❤️**
