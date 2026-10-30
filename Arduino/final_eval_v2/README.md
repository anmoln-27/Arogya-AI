#include <Wire.h>
#include <U8g2lib.h>
#include "MAX30105.h"        
#include "heartRate.h"
#include <Adafruit_MLX90640.h>
#include <Smart_ASHA_2.0_inferencing.h>

// --- SYSTEM STATES ---
enum SystemState { IDLE, SCANNING, RESULTS };
SystemState currentState = IDLE;

// --- CONFIGURATION ---
const int ecgPin = 4;   
const int gsrPin = 6; 
const float boxOffset = -9.8; 
const unsigned long SCAN_DURATION = 60000; 
unsigned long scanStartTime = 0;

// --- OBJECTS ---
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
MAX30105 pulse; 
Adafruit_MLX90640 mlx;

// --- DATA ACCUMULATORS ---
float thermalFrame[768];
long feverCount = 0, totalAiRuns = 0;
float spo2Sum = 0; int spo2Samples = 0;
int maxGsr = 0;
float finalMaxT = 0;

// Live ECG Buffer
int ecgBuffer[128];
int ecgIdx = 0;

// ECG Arrhythmia Logic
unsigned long lastRPeak = 0;
unsigned long rrIntervals[100];
int rrIdx = 0;
int ecgThreshold = 2300; // Threshold for R-Peak detection

volatile bool newThermalDataReady = false;
String currentAiLabel = "WAITING";

void tcaSelect(uint8_t i) {
  Wire.beginTransmission(0x70);
  Wire.write(1 << i);
  Wire.endTransmission();
}

// ==========================================
// CORE 0: AI BACKGROUND TASK
// ==========================================
void aiTask(void *pvParameters) {
  static float imageBuffer[768]; 
  for (;;) { 
    if (newThermalDataReady) {
      for (int i = 0; i < 768; i++) {
          float calT = thermalFrame[i] + boxOffset;
          int val = constrain(map(calT, 20, 45, 0, 255), 0, 255);
          imageBuffer[i] = (float)((val << 16) | (val << 8) | val); 
      }
      signal_t signal;
      numpy::signal_from_buffer(imageBuffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
      ei_impulse_result_t result = { 0 };
      if (run_classifier(&signal, &result, false) == EI_IMPULSE_OK) {
         float maxVal = 0; int maxIdx = 0;
         for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
             if (result.classification[i].value > maxVal) { maxVal = result.classification[i].value; maxIdx = i; }
         }
         currentAiLabel = String(result.classification[maxIdx].label);
         if (currentState == SCANNING) {
             totalAiRuns++;
             if (currentAiLabel == "Fever") feverCount++;
         }
      }
      newThermalDataReady = false;
    }
    vTaskDelay(pdMS_TO_TICKS(40));
  }
}

// ==========================================
// CORE 1: MAIN SENSORS & UI
// ==========================================
void setup() {
  disableLoopWDT(); // <-- Fixes the internal "task not found" error!
  Serial.begin(115200);
  Wire.begin(8, 18);
  Wire.setClock(100000);
  
  tcaSelect(7); u8g2.begin();
  tcaSelect(3); mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire);
  
  Wire1.begin(16, 17); 
  if(pulse.begin(Wire1)) {
      pulse.setup();
      pulse.setPulseAmplitudeRed(0x1F);
      pulse.setPulseAmplitudeIR(0x1F);
  }
  
  pinMode(ecgPin, INPUT);
  for(int i=0; i<128; i++) ecgBuffer[i] = 30;

  xTaskCreatePinnedToCore(aiTask, "AI", 16384, NULL, 1, NULL, 0);
}

void loop() {
  long ir = pulse.getIR();
  int gsr = analogRead(gsrPin);
  int ecgRaw = analogRead(ecgPin);

  switch (currentState) {
    case IDLE: {
      tcaSelect(7); u8g2.clearBuffer();
      u8g2.setFont(u8g2_font_6x12_tf);
      u8g2.drawStr(10, 20, "SMART ASHA READY");
      u8g2.drawStr(5, 40, "Finger & ECG Lead ON");
      
      // Live Signal Monitoring (Visual confirmation)
      u8g2.setFont(u8g2_font_5x7_tf);
      u8g2.setCursor(5, 58); u8g2.print("IR: "); u8g2.print(ir);
      u8g2.print(" | ECG: "); u8g2.print(ecgRaw);
      u8g2.sendBuffer();

      if (ir > 40000) { 
          currentState = SCANNING;
          scanStartTime = millis();
          feverCount = 0; totalAiRuns = 0; spo2Sum = 0; spo2Samples = 0; 
          maxGsr = 0; finalMaxT = 0; rrIdx = 0; lastRPeak = 0;
      }
      break;
    }

    case SCANNING: {
      unsigned long elapsed = millis() - scanStartTime;

      // 1. ECG Signal Processing & Graphing
      ecgBuffer[ecgIdx] = map(ecgRaw, 0, 4095, 35, 5); // Map to top half of screen
      ecgIdx = (ecgIdx + 1) % 128;

      // R-Peak detection for Arrhythmia
      if (ecgRaw > ecgThreshold) {
          unsigned long now = millis();
          if (now - lastRPeak > 250) { // Refractory period
              if (lastRPeak != 0 && rrIdx < 100) rrIntervals[rrIdx++] = now - lastRPeak;
              lastRPeak = now;
          }
      }

      // 2. Slow Data Sampling (Every 2 seconds)
      static unsigned long lastUpdate = 0;
      if (millis() - lastUpdate > 2000) {
          lastUpdate = millis();
          tcaSelect(3); mlx.getFrame(thermalFrame);
          float fMax = -99;
          for(int i=0; i<768; i++) if(thermalFrame[i] > fMax) fMax = thermalFrame[i];
          if((fMax+boxOffset) > finalMaxT) finalMaxT = fMax+boxOffset;
          newThermalDataReady = true;

          float r = (float)pulse.getRed() / (float)pulse.getIR();
          if(ir > 20000) { spo2Sum += constrain(110-(25*r), 0, 99); spo2Samples++; }
      }
      if(gsr > maxGsr) maxGsr = gsr;

      // 3. UI RENDERING (Live ECG + Progress Bar)
      tcaSelect(7);
      u8g2.clearBuffer();
      
      // Draw Live ECG Waveform
      for (int i = 0; i < 127; i++) {
          int p1 = (ecgIdx + i) % 128;
          int p2 = (ecgIdx + i + 1) % 128;
          u8g2.drawLine(i, ecgBuffer[p1], i + 1, ecgBuffer[p2]);
      }

      // Progress Area
      u8g2.setFont(u8g2_font_5x7_tf);
      u8g2.drawStr(0, 45, "DIAGNOSTIC SCAN IN PROGRESS...");
      u8g2.drawFrame(0, 50, 128, 8); 
      u8g2.drawBox(0, 50, map(elapsed, 0, SCAN_DURATION, 0, 128), 8);
      
      // Pulsing AI Label
      u8g2.setCursor(0, 63); u8g2.print("SENSORS: ACTIVE");
      u8g2.setCursor(85, 63); u8g2.print(elapsed/1000); u8g2.print("s");
      
      u8g2.sendBuffer();

      if (elapsed >= SCAN_DURATION) currentState = RESULTS;
      break;
    }

    case RESULTS: {
      float fProb = (totalAiRuns > 0) ? ((float)feverCount / totalAiRuns) * 100 : 0;
      float avgO2 = (spo2Samples > 0) ? spo2Sum / spo2Samples : 0;
      
      // Arrhythmia Analysis
      long sumRR = 0;
      for(int i=0; i<rrIdx; i++) sumRR += rrIntervals[i];
      float avgRR = (rrIdx > 0) ? (float)sumRR / rrIdx : 0;
      float var = 0;
      for(int i=0; i<rrIdx; i++) var += pow(rrIntervals[i] - avgRR, 2);
      float stdDev = (rrIdx > 1) ? sqrt(var / rrIdx) : 0;

      String cardiacLvl = "STABLE";
      if (rrIdx < 5) cardiacLvl = "NO DATA";
      else if (stdDev > 110) cardiacLvl = "ARRHYTHMIA";

      tcaSelect(7); u8g2.clearBuffer();
      u8g2.setFont(u8g2_font_6x12_tf);
      u8g2.drawStr(25, 10, "SCAN REPORT");
      u8g2.drawHLine(0, 13, 128);

      u8g2.setFont(u8g2_font_5x8_tf);
      u8g2.setCursor(0, 25); u8g2.print("FEVER:   "); u8g2.print(fProb, 0); u8g2.print("% ("); u8g2.print(finalMaxT, 1); u8g2.print("C)");
      u8g2.setCursor(0, 38); u8g2.print("OXYGEN:  "); u8g2.print(avgO2, 0); u8g2.print("%");
      u8g2.setCursor(0, 51); u8g2.print("CARDIAC: "); u8g2.print(cardiacLvl);
      u8g2.setCursor(0, 64); u8g2.print("STRESS:  "); u8g2.print((maxGsr > 3200) ? "HIGH" : "NORMAL");
      
      u8g2.drawStr(80, 64, "[RESET]");
      u8g2.sendBuffer();
      
      if (ir < 15000) currentState = IDLE;
      break;
    }
  }
  delay(10); // <-- Prevents 100% CPU lockup and lets Core 0 AI run smoothly
}
