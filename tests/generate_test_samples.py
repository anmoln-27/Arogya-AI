import numpy as np
import os

def generate_test_samples():
    test_dir = "SmartASHA_Test_Samples"
    os.makedirs(test_dir, exist_ok=True)
    
    # Normal: Background 34C, forehead 36C
    for i in range(3):
        frame = np.full((24, 32), 34.0) + np.random.uniform(-0.2, 0.2, (24, 32))
        frame[8:16, 12:20] = 36.5 + np.random.uniform(-0.3, 0.3, (8, 8))
        
        filename = os.path.join(test_dir, f"test_normal_{i}.npy")
        np.save(filename, frame)

    # Fever: Background 36.5C, forehead 39.5C
    for i in range(3):
        frame = np.full((24, 32), 36.5) + np.random.uniform(-0.2, 0.2, (24, 32))
        frame[8:16, 12:20] = 40.0 + np.random.uniform(-0.3, 0.3, (8, 8))
        
        filename = os.path.join(test_dir, f"test_fever_{i}.npy")
        np.save(filename, frame)

    print(f"[REGENERATED] 6 realistic test samples in '{test_dir}'")

if __name__ == "__main__":
    generate_test_samples()
