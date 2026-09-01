# 📂 Libs — Packaged Libraries & Dependencies

This directory contains **pre-packaged libraries**, firmware archives, and driver dependencies for the Arogya AI project.

## Contents

| File | Size | Description |
|:-----|:-----|:------------|
| `Arogya AI_Inference_Library.zip` | ~5.8 MB | Complete Edge Impulse inference library (packaged) |
| `Arogya AI_Multimodal_Dataset.zip` | ~740 KB | Compressed multimodal sensor dataset |
| `arogya-ai-cpp-mcu-v1.zip` | ~5.7 MB | C++ MCU inference library v1 (standalone) |
| `libraries/` | — | Extracted Arduino libraries for direct installation |

## Installation

### Arduino Library Installation

1. Open Arduino IDE
2. Go to **Sketch → Include Library → Add .ZIP Library**
3. Select the desired `.zip` file from this directory
4. The library will be available for `#include` in your sketches

### Manual Installation

```bash
# Extract to Arduino libraries folder
unzip Arogya AI_Inference_Library.zip -d ~/Arduino/libraries/
```

## Note

> For the latest Edge Impulse inference libraries with multi-board support, see the [`edge-impulse/`](../edge-impulse/) directory instead.
