import serial
import csv
import time
import os
import sys

# Import project config
from config import DATA_DIR

# --- CONFIGURATION ---
# Check your Arduino IDE > Tools > Port to see if this is COM4, COM6, etc.
SERIAL_PORT = 'COM3'  
BAUD_RATE = 115200
# The filename where your data will be stored
DATA_FILE = os.path.join(DATA_DIR, "environment_smoke_active.csv")

def main():
    try:
        # Initialize the Serial Connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Successfully connected to {SERIAL_PORT}.")
        print("Recording... Press Ctrl+C to stop and save the file.")

        # Open the CSV file in 'Append' mode
        with open(DATA_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            # If the file is brand new, write the header row
            if file.tell() == 0:
                writer.writerow(["Timestamp", "ECG", "GSR", "Gas", "Pulse_IR", "Temp_Max", "Label"])

            while True:
                # Read a line from the ESP32
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    # Convert the comma-separated string into a list
                    data_row = line.split(',')
                    
                    # Log to the file
                    writer.writerow(data_row)
                    
                    # Print to the screen so you can see it working
                    print(f"Captured: {data_row}")

    except serial.SerialException as e:
        print(f"Error: {e}")
        print("Double-check your COM port and make sure the Arduino Serial Monitor is CLOSED.")
    except KeyboardInterrupt:
        print("\nStopping logger... Data saved to", DATA_FILE)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()