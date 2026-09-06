/*
  Smart-ASHA: Session 2.1 - Analog Front-End (7Semi Pinout)
*/

// Updated Pins for your specific board
#define ECG_OUTPUT 4
#define ECG_LO_MINUS 5
#define ECG_LO_PLUS 6

// PSRAM Circular Buffer Setup
#define BUFFER_SIZE 2048
float* ecgBuffer;
int bufferIndex = 0;

// Filter Variables
float v[3];
float filteredECG = 0.0;

void setup() {
  Serial.begin(115200);
  
  pinMode(ECG_LO_MINUS, INPUT);
  pinMode(ECG_LO_PLUS, INPUT);
  
  // Allocate Circular Buffer in PSRAM
  if (psramFound()) {
    ecgBuffer = (float*)ps_malloc(BUFFER_SIZE * sizeof(float));
    if (ecgBuffer != NULL) {
      Serial.println("PSRAM Buffer Allocated.");
    }
  }
}

// Digital Bandpass Filter (Approx. 0.5Hz - 40Hz)
float applyBandpassFilter(float input) {
  v[0] = v[1];
  v[1] = v[2];
  v[2] = (input * 0.020083) + (v[0] * -0.919531) + (v[1] * 1.919531);
  return (v[2] - v[0]);
}

void loop() {
  // Leads-off detection
  if ((digitalRead(ECG_LO_PLUS) == 1) || (digitalRead(ECG_LO_MINUS) == 1)) {
    Serial.println("!"); // Indicates pads are not properly attached to the body
  } else {
    int rawECG = analogRead(ECG_OUTPUT);
    
    filteredECG = applyBandpassFilter((float)rawECG);

    // Store in PSRAM
    if (ecgBuffer != NULL) {
      ecgBuffer[bufferIndex] = filteredECG;
      bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    }

    // Output for Serial Plotter
    Serial.print("Raw_ECG:");
    Serial.print(rawECG);
    Serial.print(",");
    Serial.print("Filtered_ECG:");
    Serial.println(filteredECG);
  }
  delay(10); // ~100Hz sample rate
}