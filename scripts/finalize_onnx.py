import onnx
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import ONNX_MODEL_EDGE, ONNX_MODEL_FINAL

def finalize_onnx():
    src = ONNX_MODEL_EDGE
    dest = ONNX_MODEL_FINAL
    
    if not os.path.exists(src):
        # Fallback if integrated exists but edge doesn't (though names changed)
        # For simplicity, we just check the output of previous steps
        print(f"Error: {src} not found.")
        return

    print(f"Loading {src}...")
    model = onnx.load(src)
    
    print(f"Saving finalized integrated model to {dest}...")
    # This ensures all weights are absolutely contained in the .onnx binary
    onnx.save(model, dest, save_as_external_data=False)
    
    print(f"[SUCCESS] {dest} created.")

if __name__ == "__main__":
    finalize_onnx()
