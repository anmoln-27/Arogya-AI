import serial
import numpy as np
import time
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import AROGYA AI_DATASET

# --- CONFIG ---
PORT = 'COM3' # Change this to your actual COM port
BAUD = 115200
DATA_DIR = AROGYA AI_DATASET

def save_frame(raw_data, label_name):
    try:
        # Convert the 768 pixels into a 24x32 grid
        frame = np.array(raw_data, dtype=float).reshape(24, 32)
        timestamp = int(time.time() * 1000)
        filename = f"{DATA_DIR}/{label_name}/frame_{timestamp}.npy"
        np.save(filename, frame)
        print(f"Successfully saved to {label_name} folder!")
    except Exception as e:
        print(f"Error saving data: {e}")

# Main Loop
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print("--- ASHA DATA COLLECTOR ONLINE ---")
    print("Commands: [ENTER] to trigger capture, [q] to quit")

    while True:
        cmd = input("\nReady (Enter to capture, q to quit): ").strip().lower()
        if cmd == 'q':
            break
            
        # Send 'c' to trigger the Arduino
        ser.write(b'c')
        print("Trigger sent! Waiting for data...")
        
        # Wait for data
        start_time = time.time()
        captured = False
        while time.time() - start_time < 5: # 5 second timeout
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if "CAPTURE_BEGIN" in line:
                    # Extract the 768 pixels from the string
                    raw_pixels = line.replace("CAPTURE_BEGIN,", "").replace(",CAPTURE_END", "").split(",")
                    
                    # Ask you for the label
                    choice = input(f"[CAPTURE DETECTED] Save as (0=Normal, 1=Fever, d=Discard): ")
                    
                    if choice == '0':
                        save_frame(raw_pixels, "Normal")
                    elif choice == '1':
                        save_frame(raw_pixels, "Fever")
                    else:
                        print("Data discarded.")
                    captured = True
                    break
        
        if not captured and cmd != 'q':
            print("No response from sensor. Check your connections.")
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    if 'ser' in locals() and ser is not None:
        ser.close()