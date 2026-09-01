import torch
import torch.nn as nn
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import CNN_MODEL_PTH, ONNX_MODEL_EDGE
from utils.models import FeverCNN

def export_model():
    model_path = CNN_MODEL_PTH
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found. Please train the model first.")
        return

    # Load weights
    model = FeverCNN()
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()

    # Create dummy input based on our thermal frame size (1 channel, 24x32)
    dummy_input = torch.randn(1, 1, 24, 32)
    
    # Export to ONNX
    onnx_path = ONNX_MODEL_EDGE
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        export_params=True, 
        opset_version=11, 
        do_constant_folding=True,
        input_names=['input'], 
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    print(f"[SUCCESS] Custom Edge Model exported to: {onnx_path}")
    print("You can now upload this file to the 'BYOM' tab in Edge Impulse.")

if __name__ == "__main__":
    export_model()
