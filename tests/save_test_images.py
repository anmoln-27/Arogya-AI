import numpy as np
import os
from PIL import Image

def save_test_images():
    test_dir = "SmartASHA_Test_Samples"
    img_dir = "SmartASHA_Test_Images"
    os.makedirs(img_dir, exist_ok=True)
    
    if not os.path.exists(test_dir):
        print(f"Error: {test_dir} not found. Run the npy generator first.")
        return

    # Find all .npy test files
    import glob
    files = glob.glob(os.path.join(test_dir, "*.npy"))
    
    for f in files:
        data = np.load(f)
        
        # Consistent normalization (20C to 45C -> 0 to 255)
        # Using the same formula we used for training data
        norm_data = (data - 20) / (45 - 20) * 255
        norm_data = np.clip(norm_data, 0, 255).astype(np.uint8)
        
        # Convert to Image and resize for visibility (128x96)
        img = Image.fromarray(norm_data)
        img = img.resize((128, 96), resample=Image.NEAREST)
        
        basename = os.path.basename(f).replace(".npy", ".png")
        img_path = os.path.join(img_dir, basename)
        img.save(img_path)
        print(f"Image Saved: {img_path}")

    print(f"\n[DONE] Test images are ready in '{img_dir}'")

if __name__ == "__main__":
    save_test_images()
