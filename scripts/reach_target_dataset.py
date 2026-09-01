import numpy as np
import os
import glob
import time
import random

SOURCE_DIR = "SmartASHA_Dataset"
CATEGORIES = ["Normal", "Fever"]
TARGET_COUNT = 50

def augment_data():
    for cat in CATEGORIES:
        src_path = os.path.join(SOURCE_DIR, cat)
        if not os.path.exists(src_path):
            os.makedirs(src_path, exist_ok=True)
        
        files = glob.glob(os.path.join(src_path, "*.npy"))
        current_count = len(files)
        
        if current_count >= TARGET_COUNT:
            print(f"Category '{cat}' already has {current_count} frames. Skipping...")
            continue
            
        print(f"Category '{cat}' has {current_count} frames. Adding {TARGET_COUNT - current_count} augmented frames...")
        
        if current_count == 0:
            print(f"Error: Cannot augment '{cat}' because it has zero frames.")
            continue
            
        while len(glob.glob(os.path.join(src_path, "*.npy"))) < TARGET_COUNT:
            # Pick a random existing file
            f = random.choice(files)
            data = np.load(f)
            
            # Add small noise/jitter (+- 0.1 degree)
            # This simulates slight sensor variance
            jitter = (np.random.rand(*data.shape) - 0.5) * 0.2
            augmented = data + jitter
            
            timestamp = int(time.time() * 1000)
            basename = os.path.basename(f).replace(".npy", "")
            new_filename = os.path.join(src_path, f"{basename}_aug_{timestamp}.npy")
            
            np.save(new_filename, augmented)
            time.sleep(0.01) # Avoid timestamp collisions
            
    print(f"\n[DONE] Dataset now has at least {TARGET_COUNT} frames per category.")

if __name__ == "__main__":
    augment_data()
