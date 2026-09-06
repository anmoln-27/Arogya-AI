/*
 * Smart-ASHA: Final Integrated Diagnostic System
 * Hardware: ESP32-S3
 * AI Engine: Edge Impulse (TinyML)
 */

#include <Smart_ASHA_Inference.h> // Ensure this folder name matches your library install
#include <Wire.h>
#include <SPI.h>
#include "MAX30105.h"        
#include <Adafruit_MLX90640.h>

// --- PIN DEFINITIONS ---
#define PIN_CS_GSR    14
#define PIN_ECG_OUT   4
#define PIN_ECG_LO_P  6
#define PIN_ECG_LO_N  5
#define PIN_GAS_ANLG  7

// --- SENSOR CONFIGURATION ---
#define SAMPLING_FREQ_HZ 25
#define INTERVAL_MS      (1000 / SAMPLING_FREQ_HZ)

// --- OBJECTS ---
MAX30105 pulse; 
Adafruit_MLX90640 mlx;
float thermalFrame[768];
bool pulseOnline = false;
float features[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];

// Helper: TCA Hub Port Selection (0x70)
void tcaSelect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(0x70);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  // 1. Forced Serial Handshake
  Serial.begin(115200);
  unsigned long serialWait = millis();
  while (!Serial && millis() - serialWait < 5000); 

  Serial.println("\n--- SMART-ASHA: FINAL SYSTEM SYNC ---");

  // 2. I2C Bus 0 (Pins 8, 18) - The Hub Lane
  Wire.begin(8, 18);
  Wire.setClock(100000);
  Wire.setTimeOut(50);

  // Waking MPU-6050 (Hub Port 1)
  tcaSelect(1);
  Wire.beginTransmission(0x68);
  Wire.write(0x6B); Wire.write(0x00); 
  if (Wire.endTransmission() == 0) Serial.println("[OK] MPU-6050: Ready (Port 1)");

  // Starting Thermal (Hub Port 3)
  tcaSelect(3);
  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {
    mlx.setRefreshRate(MLX90640_4_HZ);
    Serial.println("[OK] Thermal Camera: Ready (Port 3)");
  }

  // 3. I2C Bus 1 (Pins 41, 42) - The Pulse Lane
  Wire1.begin(41, 42);
  Wire1.setTimeOut(50);
  if (pulse.begin(Wire1, I2C_SPEED_FAST)) {
    pulse.setup(); 
    pulseOnline = true;
    Serial.println("[OK] Pulse Sensor: Ready (Wire1)");
  }

  // 4. SPI & Analog Config
  pinMode(PIN_CS_GSR, OUTPUT); digitalWrite(PIN_CS_GSR, HIGH);
  SPI.begin(21, 39, 40, PIN_CS_GSR); 
  
  pinMode(PIN_ECG_LO_P, INPUT);
  pinMode(PIN_ECG_LO_N, INPUT);

  Serial.println("--- DIAGNOSTICS COMPLETE. STARTING INFERENCE ---\n");
}

void loop() {
  static float lastMaxTemp = 34.0;

  // --- WINDOW COLLECTION ---
  // We collect samples until the buffer is full (usually 2 seconds of data)
  for (size_t ix = 0; ix < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; ix += EI_CLASSIFIER_RAW_SAMPLES_PER_FRAME) {
    unsigned long next_tick = millis() + INTERVAL_MS;

    // A. Leads-Off Detection
    if((digitalRead(PIN_ECG_LO_P) == 1) || (digitalRead(PIN_ECG_LO_N) == 1)) {
        // Optional: Reset ECG feature or blink error LED
    }

    // B. Analog & SPI (ECG, Gas, GSR)
    int rawECG = analogRead(PIN_ECG_OUT);
    int rawGas = analogRead(PIN_GAS_ANLG);
    
    digitalWrite(PIN_CS_GSR, LOW);
    long rawGSR = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
    digitalWrite(PIN_CS_GSR, HIGH);

    // C. Pulse (Wire1)
    long irVal = (pulseOnline) ? pulse.getIR() : 0;

    // D. Motion (TCA Port 1)
    float ax = 0, ay = 0;
    tcaSelect(1);
    Wire.beginTransmission(0x68);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    if (Wire.requestFrom(0x68, 4, true) == 4) {
      int16_t rx = Wire.read() << 8 | Wire.read();
      int16_t ry = Wire.read() << 8 | Wire.read();
      ax = (float)rx / 16384.0 * 9.81;
      ay = (float)ry / 16384.0 * 9.81;
    }

    // E. Thermal (TCA Port 3 - Slow Update)
    if (ix == 0) {
      tcaSelect(3);
      if (mlx.getFrame(thermalFrame) == 0) {
        float peak = -99;
        for (int i=0; i<768; i++) if(thermalFrame[i] > peak) peak = thermalFrame[i];
        if (peak > 20) lastMaxTemp = peak;
      }
    }

    // --- FEATURE MAPPING ---
    // Mapping matches your CSV: [ECG, GSR, Gas, Pulse_IR, Temp_Max, AccelX, AccelY]
    features[ix + 0] = (float)rawECG;
    features[ix + 1] = (float)rawGSR;
    features[ix + 2] = (float)rawGas;
    features[ix + 3] = (float)irVal;
    features[ix + 4] = lastMaxTemp;
    features[ix + 5] = ax;
    features[ix + 6] = ay;

    // Progress bar for Serial Monitor
    if (ix % (EI_CLASSIFIER_RAW_SAMPLES_PER_FRAME * 5) == 0) Serial.print(".");

    // Maintain 40ms loop timing
    while (millis() < next_tick);
  }

  // --- TINYML INFERENCE ---
  Serial.print(" Analyzing...");
  signal_t signal;
  numpy::signal_from_buffer(features, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);

  ei_impulse_result_t result = { 0 };
  EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);

  if (res == EI_IMPULSE_OK) {
    Serial.println("\n\n>>> SMART-ASHA STATUS REPORT <<<");
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
      Serial.printf("  [%s]: %.3f\n", result.classification[ix].label, result.classification[ix].value);
    }
    
    // Quick-Alert Logic
    if (result.classification[2].value > 0.8) { // Assuming index 2 is 'Hazard'
        Serial.println("!!! ALERT: ENVIRONMENTAL SMOKE DETECTED !!!");
    }
    Serial.println("--------------------------------\n");
  } else {
    Serial.printf("ERR: Inference Failed (%d)\n", res);
  }
}
