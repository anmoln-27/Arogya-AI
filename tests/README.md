# 📂 Tests — Verification & Validation

This directory contains scripts for **testing and verifying** model performance and data integrity.

## Scripts

| Script | Description | Usage |
|:-------|:------------|:------|
| `generate_test_samples.py` | Generate synthetic test samples from the dataset | `python tests/generate_test_samples.py` |
| `save_test_images.py` | Save thermal arrays as PNG images for visual inspection | `python tests/save_test_images.py` |
| `verify_test_samples.py` | Run model inference on test samples and report accuracy | `python tests/verify_test_samples.py` |

## Running All Tests

```bash
# From project root:
python tests/verify_test_samples.py
```

## Expected Output

```
Testing fever_model_final.onnx on SmartASHA_Test_Samples...

Sample 001: Prediction=Healthy, Confidence=98.3%  ✓
Sample 002: Prediction=Fever,   Confidence=99.1%  ✓
...
Overall Accuracy: 100% (50/50)
```
