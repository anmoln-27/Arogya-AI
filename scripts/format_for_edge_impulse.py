import numpy as np
import os
import glob
from PIL import Image

# Directories
SOURCE_DIR = "SmartASHA_Dataset"
TARGET_DIR = "edge_impulse_format"
CATEGORIES = {"Normal": "Healthy", "Fever": "Fever"}

def process_to_images():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} not found.")
        return

    print("Reorganizing and converting data for Edge Impulse...")
    
    total_processed = 0
    for src_cat, target_cat in CATEGORIES.items():
        src_path = os.path.join(SOURCE_DIR, src_cat)
        dest_path = os.path.join(TARGET_DIR, target_cat)
        
        if not os.path.exists(src_path):
            print(f"Warning: Category folder {src_path} not found. Skipping...")
            continue
            
        os.makedirs(dest_path, exist_ok=True)
        
        files = glob.glob(os.path.join(src_path, "*.npy"))
        for f in files:
            try:
                data = np.load(f)
                
                # Normalize to 0-255 for image format
                # We use a fixed range (20C to 45C) so that 'hot' actually looks 'hot' 
                # consistently across different captures.
                norm_data = (data - 20) / (45 - 20) * 255
                norm_data = np.clip(norm_data, 0, 255).astype(np.uint8)
                
                # Scale up from 24x32 to 96x128 for easier viewing
                # (Edge Impulse will resize it anyway, but it helps for human inspection)
                img = Image.fromarray(norm_data)
                img = img.resize((128, 96), resample=Image.NEAREST)
                
                basename = os.path.basename(f).replace(".npy", ".png")
                img.save(os.path.join(dest_path, basename))
                total_processed += 1
            except Exception as e:
                print(f"Error processing {f}: {e}")
            
    print(f"\n[SUCCESS] Reorganized {total_processed} frames into '{TARGET_DIR}' folder.")
    print("Folder structure:")
    print(f"  - {TARGET_DIR}/Healthy")
    print(f"  - {TARGET_DIR}/Fever")
    print("\nYou can now zip this folder and upload it directly to Edge Impulse!")

if __name__ == "__main__":
    process_to_images()
