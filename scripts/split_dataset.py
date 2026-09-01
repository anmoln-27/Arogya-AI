import os
import glob
import csv
import math

def split_csv(filepath, train_dir, test_dir, split_ratio=0.8):
    basename = os.path.basename(filepath)
    
    with open(filepath, 'r') as f:
        reader = list(csv.reader(f))
        
    if not reader:
        return
        
    header = reader[0]
    data = reader[1:]
    
    # Calculate the split index for 80/20 temporal split
    split_index = math.floor(len(data) * split_ratio)
    train_data = data[:split_index]
    test_data = data[split_index:]
    
    # Save training data
    train_path = os.path.join(train_dir, basename)
    with open(train_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(train_data)
        
    # Save testing data
    test_path = os.path.join(test_dir, basename)
    with open(test_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(test_data)
        
    print(f"Split {basename}: {len(train_data)} train rows, {len(test_data)} test rows.")

if __name__ == "__main__":
    input_dir = "edge_impulse_format"
    train_dir = os.path.join(input_dir, "training")
    test_dir = os.path.join(input_dir, "testing")
    
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    csv_files = glob.glob(os.path.join(input_dir, "*.data.csv"))
    
    print("Splitting datasets 80/20 (Train/Test)...")
    for file in csv_files:
        split_csv(file, train_dir, test_dir)
        
    print(f"\nDone! Datasets have been divided into:\n- {train_dir}\n- {test_dir}")
