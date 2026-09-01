import os

# Base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory structure
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
UTILS_DIR = os.path.join(BASE_DIR, "utils")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
LIBS_DIR = os.path.join(BASE_DIR, "libs")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

# Ensure critical directories exist
for directory in [DATA_DIR, DATASETS_DIR, MODELS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Specific dataset paths
AROGYA AI_DATASET = os.path.join(DATASETS_DIR, "SmartASHA_Dataset")
TEST_IMAGES_DIR = os.path.join(DATASETS_DIR, "SmartASHA_Test_Images")
TEST_SAMPLES_DIR = os.path.join(DATASETS_DIR, "SmartASHA_Test_Samples")

# Model filenames
CNN_MODEL_PTH = os.path.join(MODELS_DIR, "fever_cnn_model.pth")
ONNX_MODEL_EDGE = os.path.join(MODELS_DIR, "fever_model_edge.onnx")
ONNX_MODEL_FINAL = os.path.join(MODELS_DIR, "fever_model_final.onnx")
