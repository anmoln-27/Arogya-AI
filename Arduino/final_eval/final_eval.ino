/*
 * Smart ASHA v10.7: Final Integrated Clinical System (Pro UI Edition)
 * Core 0: AI Inference (Anemia & Fever)
 * Core 1: Mutex-Protected Sensor Polling & UI
 */

#include <Smart_ASHA_2.0_inferencing.h>
#include <Wire.h>
#include <U8g2lib.h>
#include "MAX30105.h"        
#include "heartRate.h"
#include <Adafruit_MLX90640.h>
#include <Adafruit_AS7343.h> 

// --- PIN STRUCTURE ---
const int ecgPin = 4;   
const int gasPin = 6; 
const float boxOffset = -9.8; 
const unsigned long SCAN_DURATION = 60000; 

// --- SYSTEM STATES ---
enum SystemState { IDLE, SCANNING, RESULTS };
SystemState currentState = IDLE;
unsigned long scanStartTime = 0;

// --- OBJECTS ---
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
MAX30105 pulse; 
Adafruit_MLX90640 mlx;
Adafruit_AS7343 as7343;
bool mlxOnline = false, asOnline = false, pulseOnline = false;

// --- MUTEX & SHARED DATA ---
SemaphoreHandle_t i2cMutex;
float thermalFrame[768] __attribute__((aligned(32)));
uint16_t specReadings[18];
volatile bool newAiDataReady = false;

// --- VITALS ACCUMULATORS & LIVE STATS ---
long feverCount = 0, totalAiRuns = 0;
float spo2Sum = 0; int spo2Samples = 0;
long f5Sum = 0; int specSamples = 0;
long gasSum = 0; int gasSamples = 0; int peakGas = 0;

// Live UI Variables
float currentBPM = 0, currentTemp = 0;
int currentSpO2 = 0;

// ECG Graph & Logic
int ecgBuffer[128];
int ecgIdx = 0;
unsigned long lastRPeak = 0;
unsigned long rrIntervals[100];
int rrIdx = 0;

void tcaSelect(uint8_t i) {
  Wire.beginTransmission(0x70);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void tcaDeselect() {
  Wire.beginTransmission(0x70);
  Wire.write(0);
  Wire.endTransmission();
}

// ==========================================
// CORE 0: AI PROCESSING (FEVER & ANEMIA)
// ==========================================
void aiTask(void *pvParameters) {
  for (;;) {
    if (newAiDataReady) {
      float imageBuffer[768];
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
             if (result.classification[i].value > maxVal) { 
                 maxVal = result.classification[i].value; 
                 maxIdx = i; 
             }
         }
         if (currentState == SCANNING) {
             totalAiRuns++;
             if (String(result.classification[maxIdx].label) == "Fever") feverCount++;
         }
      }
      newAiDataReady = false;
    }
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}

// ==========================================
// SETUP
// ==========================================
void setup() {
  disableLoopWDT();
  Serial.begin(115200);
  i2cMutex = xSemaphoreCreateMutex();
  
  Wire.begin(8, 18);
  Wire.setClock(50000);

  tcaSelect(7); u8g2.begin();
  tcaSelect(3); mlxOnline = mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire);
  
  tcaSelect(4); 
  if(as7343.begin()) {
      as7343.setGain(AS7343_GAIN_128X);
      as7343.setATIME(100);  
      as7343.setASTEP(999);  
      asOnline = true;
  }

  Wire1.begin(16, 17);
  if(pulse.begin(Wire1)) {
    pulse.setup();
    pulse.setPulseAmplitudeRed(0x3F); 
    pulse.setPulseAmplitudeIR(0x3F);
    pulseOnline = true;
  }

  pinMode(ecgPin, INPUT);
  pinMode(gasPin, INPUT);
  for(int i=0; i<128; i++) ecgBuffer[i] = 30;

  xTaskCreatePinnedToCore(aiTask, "AI", 16384, NULL, 1, NULL, 0);
  tcaDeselect();
}

// ==========================================
// MAIN LOOP
// ==========================================
void loop() {
  long ir = pulse.getIR();
  int ecgRaw = analogRead(ecgPin);
  int gasRaw = analogRead(gasPin);

  // Live BPM Calculation for UI
  if (checkForBeat(ir)) {
    static unsigned long lastBeat = 0;
    currentBPM = 60000 / (millis() - lastBeat);
    lastBeat = millis();
  }

  switch (currentState) {
    case IDLE:
      if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(100))) {
        tcaSelect(7);
        u8g2.clearBuffer();
        u8g2.setFont(u8g2_font_6x12_tf);
        u8g2.drawStr(15, 25, "SMART ASHA READY");
        u8g2.setFont(u8g2_font_5x7_tf);
        u8g2.drawStr(5, 45, "Insert Finger & Blow");
        u8g2.sendBuffer();
        tcaDeselect();
        xSemaphoreGive(i2cMutex);
      }
      
      if (ir > 14000) { 
        currentState = SCANNING; 
        scanStartTime = millis();
        feverCount = 0; totalAiRuns = 0; 
        spo2Sum = 0; spo2Samples = 0; 
        gasSum = 0; gasSamples = 0; peakGas = 0;
        f5Sum = 0; specSamples = 0; rrIdx = 0; lastRPeak = 0;
        currentBPM = 0; currentTemp = 0; currentSpO2 = 0;
      }
      break;

    case SCANNING:
      // 1. HIGH SPEED ANALOG (No Mutex)
      // Map ECG to the middle of the screen (Y: 15 to 48) to leave room for headers
      ecgBuffer[ecgIdx] = map(ecgRaw, 0, 4095, 48, 15); 
      ecgIdx = (ecgIdx + 1) % 128;
      
      if (ecgRaw > 2300 && (millis() - lastRPeak > 250)) {
          if (lastRPeak != 0 && rrIdx < 100) rrIntervals[rrIdx++] = millis() - lastRPeak;
          lastRPeak = millis();
      }
      
      gasSum += gasRaw; gasSamples++;
      if(gasRaw > peakGas) peakGas = gasRaw;

      // 2. SEQUENCED I2C & UI RENDER (Mutex Protected)
      static unsigned long lastMux = 0;
      if (millis() - lastMux > 1500) {
        lastMux = millis();
        
        // Quick Live SpO2 update
        if(ir > 8000 && pulseOnline) { 
            float r = (float)pulse.getRed() / (float)ir;
            currentSpO2 = constrain(110-(25*r), 85, 99);
            spo2Sum += currentSpO2; spo2Samples++; 
        }

        if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(500))) {
          
          if (mlxOnline) {
            tcaSelect(3); 
            if(mlx.getFrame(thermalFrame) == 0){
               float mt = -99;
               for(int i=0; i<768; i++) if(thermalFrame[i] > mt) mt = thermalFrame[i];
               currentTemp = mt + boxOffset;
            }
          }
          
          if (asOnline) {
            tcaSelect(4); 
            if (as7343.readAllChannels(specReadings)) {
                f5Sum += specReadings[5]; 
                specSamples++;
            }
          }
          
          // --- LIVE SCANNING UI ---
          tcaSelect(7); 
          u8g2.clearBuffer();
          u8g2.setFont(u8g2_font_5x7_tf);
          
          // Header Row
          u8g2.setCursor(0, 8); u8g2.print("BPM:"); u8g2.print((int)currentBPM);
          u8g2.setCursor(45, 8); u8g2.print("O2:"); u8g2.print(currentSpO2); u8g2.print("%");
          u8g2.setCursor(85, 8); u8g2.print("T:"); u8g2.print(currentTemp, 1); u8g2.print("C");
          u8g2.drawHLine(0, 11, 128);

          // ECG Graph
          for (int i=0; i<127; i++) {
              u8g2.drawLine(i, ecgBuffer[(ecgIdx+i)%128], i+1, ecgBuffer[(ecgIdx+i+1)%128]);
          }

          // Footer & Progress
          u8g2.drawFrame(0, 52, 128, 8); 
          u8g2.drawBox(0, 52, map(millis()-scanStartTime, 0, SCAN_DURATION, 0, 128), 8);
          u8g2.setCursor(0, 64); u8g2.print("SCANNING VITALS...");
          
          u8g2.sendBuffer();
          tcaDeselect();
          xSemaphoreGive(i2cMutex);
          newAiDataReady = true; 
        }
      }

      if (millis() - scanStartTime >= SCAN_DURATION) currentState = RESULTS;
      break;

    case RESULTS:
      if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(500))) {
          // --- CALCULATIONS ---
          float fProb = (totalAiRuns > 0) ? ((float)feverCount / totalAiRuns) * 100 : 0;
          float avgO2 = (spo2Samples > 0) ? spo2Sum / spo2Samples : 0;
          float avgGas = (gasSamples > 0) ? (float)gasSum / gasSamples : 0;
          float avgF5 = (specSamples > 0) ? (float)f5Sum / specSamples : 0;
          
          long sumRR = 0; for(int i=0; i<rrIdx; i++) sumRR += rrIntervals[i];
          float avgRR = (rrIdx > 0) ? (float)sumRR/rrIdx : 0;
          float var = 0; for(int i=0; i<rrIdx; i++) var += pow(rrIntervals[i]-avgRR, 2);
          float stdDev = (rrIdx > 1) ? sqrt(var/rrIdx) : 0;
          
          String cardiac = (stdDev > 115) ? "ARRHYTHMIA" : "STABLE";
          if (rrIdx < 5) cardiac = "NO DATA";
          String anemia = (avgF5 > 1500) ? "RISK" : "NORMAL"; 
          String resp = (peakGas - avgGas < 300) ? "RISK" : "GOOD";

          // --- FINAL CLINICAL DASHBOARD UI ---
          tcaSelect(7);
          u8g2.clearBuffer();
          
          // Header
          u8g2.setFont(u8g2_font_6x12_tf);
          u8g2.drawStr(15, 10, "CLINICAL REPORT");
          u8g2.drawHLine(0, 13, 128);

          // 2-Column Grid
          u8g2.setFont(u8g2_font_5x8_tf);
          
          // Column 1 (Left)
          u8g2.setCursor(0, 26); u8g2.print("FEVER: "); u8g2.print(fProb > 60 ? "YES" : "NO");
          u8g2.setCursor(0, 40); u8g2.print("O2:    "); u8g2.print(avgO2, 0); u8g2.print("%");
          u8g2.setCursor(0, 54); u8g2.print("RESP:  "); u8g2.print(resp);

          // Column 2 (Right)
          u8g2.setCursor(70, 26); u8g2.print("HRT:"); u8g2.print(cardiac);
          u8g2.setCursor(70, 40); u8g2.print("ANM:"); u8g2.print(anemia);

          // Footer
          u8g2.drawHLine(0, 56, 128);
          u8g2.setFont(u8g2_font_4x6_tf);
          u8g2.drawStr(20, 64, "[ REMOVE FINGER TO EXIT ]");
          
          u8g2.sendBuffer();
          tcaDeselect();
          xSemaphoreGive(i2cMutex);
      }
      
      if (ir < 15000) currentState = IDLE; 
      break;
  }
  delay(10);
}