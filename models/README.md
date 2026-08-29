# 📂 Models — Trained Weights & Exports

This directory contains **trained model weights** and exported inference-ready model files.

## Model Card — FeverCNN

| Property | Value |
|:---------|:------|
| **Name** | FeverCNN |
| **Task** | Binary Classification (Fever vs Healthy) |
| **Input** | 1 × 24 × 32 (Grayscale Thermal Image) |
| **Architecture** | 2× Conv2D (8→16 filters, 3×3, ReLU, MaxPool) → Flatten → Dense(32) → Dense(2) |
| **Parameters** | ~14K |
| **Framework** | PyTorch → ONNX |
| **Target Hardware** | ESP32-S3, Arduino Nano 33 BLE Sense |

## Files

| File | Format | Size | Description |
|:-----|:-------|:-----|:------------|
| `fever_cnn_model.pth` | PyTorch | ~105 KB | Full PyTorch checkpoint (weights + optimizer state) |
| `fever_model_final.onnx` | ONNX | ~120 KB | Finalized ONNX model with integrated weights |
| `fever_model_integrated.onnx` | ONNX | ~120 KB | Integrated ONNX (weights embedded in graph) |
| `fever_model_edge.onnx` | ONNX | ~17 KB | Edge-optimized ONNX (external data file) |
| `fever_model_edge.onnx.data` | Binary | ~101 KB | External weight data for edge ONNX model |

## Performance

| Class | Accuracy | Avg. Confidence |
|:------|:---------|:----------------|
| **Healthy** | 100% | 98.01% |
| **Fever** | 100% | 99.27% |

## Usage

### Load in PyTorch

```python
from utils.models import get_model
import torch

model = get_model()
model.load_state_dict(torch.load("models/fever_cnn_model.pth"))
model.eval()
```

### Load in ONNX Runtime

```python
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("models/fever_model_final.onnx")
input_name = session.get_inputs()[0].name
result = session.run(None, {input_name: np.random.randn(1, 1, 24, 32).astype(np.float32)})
```
