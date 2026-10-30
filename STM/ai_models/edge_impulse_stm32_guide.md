# 🧠 Edge-AI Model Deployment Guide: Cortex-M33 & CMSIS-NN
## Porting the Smart-ASHA 2D-CNN Thermal Vision Model to STM32H533RE

This guide details the procedure for exporting, compiling, and running the **Smart-ASHA 2D-CNN Fever & Thermal Anomaly Detection model** on the **Arm® Cortex®-M33** core of the STM32H533RE.

---

### 1. Model Specifications & Quantization Target

| Model Parameter | ESP32-S3 Baseline | STM32H533RE Target | Engineering Justification |
| :--- | :--- | :--- | :--- |
| **Input Tensor Shape** | $1 \times 24 \times 32 \times 1$ (768 pixels)| $1 \times 24 \times 32 \times 1$ | Identical input from MLX90640 Far-IR camera |
| **Quantization Format**| Float32 / INT8 | **Strictly INT8 (Quantized)** | Conserves Flash (< 35 KB) and accelerates SIMD |
| **Math Accelerator** | Xtensa PIE SIMD | **Arm Helium / DSP + FPU** | Hardware multiply-accumulate (MAC) instructions |
| **Inference Engine** | Edge Impulse C++ SDK | **CMSIS-NN / STM32Cube.AI** | Native optimized Arm kernel acceleration |
| **Inference Latency** | ~110 ms | **< 90 ms** | 250 MHz Cortex-M33 clock executes faster |
| **RAM Tensor Arena** | ~65 KB | **~38 KB (with arena reuse)**| Fits easily inside STM32H533RE's 272 KB SRAM |

---

### 2. Exporting from Edge Impulse Studio for STM32

1. Navigate to your **Edge Impulse Project Dashboard** (`Smart_ASHA_2.0`).
2. Go to **Deployment** on the left menu.
3. In the search box, choose **C++ Library** or **STM32Cube.AI package**.
4. Under **Select optimizations**:
   * Choose **Quantized (int8)** (Mandatory: do not select Float32 to stay within the 512 KB Flash limit).
   * Enable **CMSIS-NN optimizations**.
5. Click **Build** to download the compiled `.zip` library.
6. Extract the library into `STM/firmware/Smart_ASHA_STM32H533RE/src/`.

---

### 3. Alternative: Deploying via STM32Cube.AI (X-CUBE-AI)

If you are using **STM32CubeIDE**:
1. Open the `.ioc` pinout and configuration file in STM32CubeMX.
2. Under **Software Packs** -> **Select Components**, enable **STMicroelectronics.X-CUBE-AI**.
3. Under **Artificial Intelligence**, click **Add network**:
   * Name: `fever_cnn`
   * Model type: **ONNX** or **TFLite** (select `models/fever_model_edge.onnx` from the project repository).
   * Compression: **4× or 8× (INT8 Quantization)**.
4. Click **Analyze**:
   * The tool reports exact Flash usage, SRAM usage, and projected MACC cycles on the Cortex-M33 @ 250 MHz.
5. Click **Generate Code** to integrate the inference runtime directly into your project.

---

### 4. Code Integration Example (CMSIS-NN C++ Wrapper)

```cpp
#include "edge-impulse-sdk/classifier/ei_run_classifier.h"

// 768-pixel thermopile raw frame input
extern float thermalFrame[768];

void runThermalInference() {
    // 1. Normalize and pack into INT8 feature buffer
    static int8_t quantized_features[768];
    for (int i = 0; i < 768; i++) {
        float tempC = thermalFrame[i];
        // Scale temperature range [20.0C, 45.0C] into [-128, 127]
        quantized_features[i] = (int8_t)constrain(((tempC - 20.0f) / 25.0f * 255.0f) - 128.0f, -128, 127);
    }

    // 2. Wrap buffer into an Edge Impulse signal structure
    signal_t signal;
    signal.total_length = 768;
    signal.get_data = &get_signal_data; // Callback function

    // 3. Execute inference using CMSIS-NN DSP acceleration
    ei_impulse_result_t result = { 0 };
    EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);

    if (res == EI_IMPULSE_OK) {
        Serial.printf("[AI] Classification: %s (Confidence: %.2f%%)\n",
            result.classification[0].label,
            result.classification[0].value * 100.0f
        );
    }
}
```

