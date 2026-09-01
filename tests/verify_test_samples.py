import torch
import torch.nn as nn
import numpy as np
import os
import glob
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import CNN_MODEL_PTH, TEST_SAMPLES_DIR
from utils.models import FeverCNN

def run_verification():
    # 1. Load Model
    model = FeverCNN()
    if not os.path.exists(CNN_MODEL_PTH):
        print(f"Error: {CNN_MODEL_PTH} not found. Please train the model first.")
        return
        
    model.load_state_dict(torch.load(CNN_MODEL_PTH, map_location=torch.device('cpu')))
    model.eval()
    
    # 2. Get Test Files
    test_files = glob.glob(os.path.join(TEST_SAMPLES_DIR, "*.npy"))
    
    print("--- MODEL VERIFICATION REPORT ---")
    print(f"{'Filename':<30} | {'Prediction':<10} | {'Confidence':<10}")
    print("-" * 55)
    
    correct_normals = 0
    correct_fevers = 0
    
    for f in test_files:
        data = np.load(f)
        
        # Preprocess exactly like training
        # (frame - 20) / 25.0
        input_tensor = (data - 20) / 25.0
        input_tensor = torch.FloatTensor(input_tensor).unsqueeze(0).unsqueeze(0) # (1, 1, 24, 32)
        
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            label = "FEVER" if predicted.item() == 1 else "HEALTHY"
            conf_val = confidence.item() * 100
            
            print(f"{os.path.basename(f):<30} | {label:<10} | {conf_val:>8.2f}%")
            
            # Simple tracking
            if "normal" in f and label == "HEALTHY": correct_normals += 1
            if "fever" in f and label == "FEVER": correct_fevers += 1

    print("-" * 55)
    print(f"Summary: Healthy Accuracy: {correct_normals}/3 | Fever Accuracy: {correct_fevers}/3")

if __name__ == "__main__":
    run_verification()
