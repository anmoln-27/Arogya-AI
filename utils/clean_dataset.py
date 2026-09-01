import os
import glob
import csv

def is_valid_number(val):
    try:
        num = float(val)
        if abs(num) > 100000:
            return False, num
        return True, num
    except ValueError:
        return True, val

def clean_csv(filepath):
    basename = os.path.basename(filepath)
    
    with open(filepath, 'r') as f:
        reader = list(csv.DictReader(f))
        
    if not reader:
        return
    
    fieldnames = reader[0].keys()
    
    # --- 1. Find Min/Max Timestamp for Cropping ---
    min_ts = None
    max_ts = None
    for row in reader:
        try:
            ts = float(row['timestamp'])
            if min_ts is None or ts < min_ts:
                min_ts = ts
            if max_ts is None or ts > max_ts:
                max_ts = ts
        except:
            pass

    if min_ts is None or max_ts is None:
        print(f"[{basename}] Could not find valid timestamps. Skipping.")
        return

    # Temporal Cropping Constraints: 5 seconds at start, 10 seconds at end
    start_time = min_ts + 5000
    end_time = max_ts - 10000
    
    duration = max_ts - min_ts
    if duration <= 15000:
        print(f"[{basename}] Duration too short to crop ({duration}ms). Skipping crop.")
        start_time = min_ts
        end_time = max_ts

    cleaned_data = []
    dropped_tails = 0
    anomalies_fixed = 0
    
    prev_row = None
    
    for row in reader:
        try:
            ts = float(row['timestamp'])
        except:
            continue
            
        # --- 2. Temporal Cropping ---
        if ts < start_time or ts > end_time:
            dropped_tails += 1
            continue
            
        # --- 3. Hardware Artifact Cleanup (GIGO Prevention) ---
        clean_row = {}
        for key in fieldnames:
            val = row[key]
            
            # Don't touch timestamp
            if key == 'timestamp':
                clean_row[key] = val
                continue
                
            is_valid, num = is_valid_number(val)
            if not is_valid:
                # E.g. jumped to 3 Lakhs
                anomalies_fixed += 1
                if prev_row is not None and key in prev_row:
                    clean_row[key] = prev_row[key] # Forward fill
                else:
                    clean_row[key] = "0" # Fallback
            else:
                clean_row[key] = val
                
        cleaned_data.append(clean_row)
        prev_row = clean_row
        
    # Overwrite the file
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)
        
    print(f"[{basename}] Cleaned! Cropped {dropped_tails} tail rows. Fixed {anomalies_fixed} hardware spikes. Remaining rows: {len(cleaned_data)}")

if __name__ == "__main__":
    input_dir = "edge_impulse_format"
    csv_files = glob.glob(os.path.join(input_dir, "*.data.csv"))
    
    print("Starting Automated Data Cleaning...")
    for file in csv_files:
        clean_csv(file)
    print("Data Cleaning Complete!")
