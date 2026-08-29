import onnx
import os

def integrate_weights():
    src = "fever_model_edge.onnx"
    dest = "fever_model_integrated.onnx"
    
    if not os.path.exists(src):
        print(f"Error: {src} not found.")
        return

    print(f"Loading {src}...")
    model = onnx.load(src)
    
    print(f"Saving integrated model to {dest}...")
    # save_as_external_data=False ensures all weights are embedded in the .onnx file
    onnx.save(model, dest, save_as_external_data=False)
    
    if os.path.exists(dest):
        print(f"[SUCCESS] Model weights integrated! Use '{dest}' for Edge Impulse.")
    else:
        print("Error: Failed to save integrated model.")

if __name__ == "__main__":
    integrate_weights()
