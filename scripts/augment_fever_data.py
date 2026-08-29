import numpy as np
import os
import glob
import time
import random

NORMAL_DIR = "SmartASHA_Dataset/Normal"
FEVER_DIR = "SmartASHA_Dataset/Fever"

def augment_to_fever():
    # Find all captured normal frames
    files = glob.glob(f"{NORMAL_DIR}/*.npy")
    
    if not files:
        print("No normal data found to augment. Capture some normal frames first!")
        return

    print(f"Found {len(files)} files. Generating synthetic fever data...")

    for file_path in files:
        # Load the normal frame
        frame = np.load(file_path)
        
        # DATA CALIBRATION:
        # We add a random offset between 3.0 and 4.5 degrees Celsius 
        # to simulate the shift from healthy forehead temp to fever.
        offset = random.uniform(3.0, 4.5)
        fever_frame = frame + offset
        
        # Save to Fever directory
        timestamp = int(time.time() * 1000)
        filename = f"{FEVER_DIR}/synth_fever_{timestamp}.npy"
        np.save(filename, fever_frame)
        
        print(f"[OK] Generated: {os.path.basename(filename)} (Offset: +{offset:.2f}C)")
        time.sleep(0.01) # Prevent filename collisions

if __name__ == "__main__":
    # Ensure Fever directory exists
    os.makedirs(FEVER_DIR, exist_ok=True)
    augment_to_fever()
