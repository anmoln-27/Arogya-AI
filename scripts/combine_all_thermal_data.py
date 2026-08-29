import numpy as np
import os
import glob

def compile_all_data():
    source_dir = "SmartASHA_Dataset"
    normal_files = glob.glob(os.path.join(source_dir, "Normal", "*.npy"))
    fever_files = glob.glob(os.path.join(source_dir, "Fever", "*.npy"))
    
    all_files = normal_files + fever_files
    print(f"Combining {len(all_files)} total thermal frames...")
    
    all_data = []
    
    for f in all_files:
        try:
            data = np.load(f)
            # Add channel dimension to match model input (1, 24, 32)
            if data.ndim == 2:
                data = data[np.newaxis, :, :]
            all_data.append(data)
        except Exception as e:
            print(f"Error loading {f}: {e}")
            
    if not all_data:
        print("No data found!")
        return
        
    # Stack into one large array of shape (N, 1, 24, 32)
    final_array = np.stack(all_data)
    
    # Shuffle the data to ensure balanced representation
    np.random.shuffle(final_array)
    
    output_filename = "representative_thermal_data.npy"
    np.save(output_filename, final_array)
    
    print(f"\n[SUCCESS] Compiled data shape: {final_array.shape}")
    print(f"Saved to: {output_filename}")
    print("You can now upload this file to Edge Impulse Step 3 for quantization.")

if __name__ == "__main__":
    compile_all_data()
