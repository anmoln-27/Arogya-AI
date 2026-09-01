import serial
import numpy as np
import time
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import AROGYA AI_DATASET

PORT = 'COM3'
BAUD = 115200
DATA_DIR = os.path.join(AROGYA AI_DATASET, "Normal")
DURATION_SEC = 120  # 2 minutes
INTERVAL_SEC = 5    # Capture every 5 seconds

def save_frame(raw_data):
    try:
        frame = np.array(raw_data, dtype=float).reshape(24, 32)
        timestamp = int(time.time() * 1000)
        filename = f"{DATA_DIR}/frame_{timestamp}.npy"
        np.save(filename, frame)
        print(f"[SAVED] {filename}")
    except Exception as e:
        print(f"Error saving: {e}")

try:
    os.makedirs(DATA_DIR, exist_ok=True)
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"--- AUTO-COLLECTOR STARTED ---")
    print(f"Goal: {DURATION_SEC} seconds of collection, every {INTERVAL_SEC}s.")
    
    start_time = time.time()
    last_capture = 0
    
    while time.time() - start_time < DURATION_SEC:
        current_time = time.time()
        
        # Trigger every 5 seconds
        if current_time - last_capture >= INTERVAL_SEC:
            ser.write(b'c')
            last_capture = current_time
            
            # Wait for response
            capture_start = time.time()
            while time.time() - capture_start < 3: # 3s timeout per frame
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if "CAPTURE_BEGIN" in line:
                        raw_pixels = line.replace("CAPTURE_BEGIN,", "").replace(",CAPTURE_END", "").split(",")
                        save_frame(raw_pixels)
                        break
        time.sleep(0.1) # Small sleep to reduce CPU usage
        
    print("--- AUTO-COLLECTOR COMPLETE ---")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'ser' in locals() and ser is not None: 
        ser.close()
