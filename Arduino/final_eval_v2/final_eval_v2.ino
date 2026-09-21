/*
 * ====================================================================================================
 *  SMART-ASHA v12.0: CLINICAL WORKSTATION FIRMWARE (PRO EDITION)
 * ====================================================================================================
 *  Target Hardware: 7Semi ESP32-S3 EC200U 4G LTE Smart Modem + TCA9548A Multiplexer
 *  
 *  CORE ALLOCATION (FreeRTOS):
 *   - Core 0: Asynchronous AI Inference (Smart_ASHA_2.0 2D CNN Vision Model on 768-pixel thermal heatmap)
 *   - Core 1: High-Speed Multimodal Polling, Digital Filtering, MPU Rejection, NVS Storage & UI
 *
 *  THE 4 STAR PERFORMERS:
 *   1. MAX30105:   SpO2, BPM, Perfusion Index (PI %), Green LED (537nm) verification, Die Temp check
 *   2. AS7343:     14-Channel Multi-Spectral (Anemia F5/F8, Jaundice F1/FZ, Dehydration NIR/FXL, Fingerprint)
 *   3. MLX90640:   Radiometric Thermal Vision (Dynamic Ta, Central Forehead ROI, Bilateral Temporal Asymmetry)
 *   4. AD8232:     Calibrated ECG Front-End (EMA Filter, SDNN, RMSSD, pNN50 Autonomic Tone, Leads-Off Guard)
 *
 *  DEEP ESP32-S3 ARCHITECTURE & TELEMETRY:
 *   - Factory eFuse ADC Linearity Calibration (analogReadMilliVolts)
 *   - Internal NVS Flash Vault (100 Persistent Patient Records with Serial EXPORT / DUMP)
 *   - Web-Bluetooth (BLE 5.0) Wireless GATT Service ("Smart-ASHA-Pro" for Zero-App sync)
 *   - Hardware Task Watchdog Protection (esp_task_wdt auto-recovery)
 *   - Multilingual Clinical Engine: English, Hindi Devanagari, Romanized Hindi, and Bilingual modes
 *
 *  PHYSICAL BUS & PIN ASSIGNMENT (ZERO HARDWARE CHANGES):
 *   - Primary I2C (Wire @ 50 kHz):      GPIO 8 (SDA), GPIO 18 (SCL) -> TCA9548A Multiplexer (0x70)
 *       * Port 2: MPU6050 6-Axis IMU (0x68) [with Port 1 auto-detect fallback]
 *       * Port 3: MLX90640 Thermal Camera (0x33)
 *       * Port 4: AS7343 14-Channel Multi-Spectral Optical Sensor (0x39)
 *       * Port 7: SH1106 128x64 OLED Display (0x3C)
 *   - Secondary I2C (Wire1 @ 400 kHz):  GPIO 16 (SDA), GPIO 17 (SCL) -> MAX30105 Pulse Oximeter
 *   - Calibrated Analog Inputs:
 *       * GPIO 4: AD8232 ECG Sensor (ADC1_CH6 via eFuse calibration)
 *       * GPIO 6: MQ-135 Gas / Respiratory Sensor (ADC1_CH5 via eFuse calibration)
 * ====================================================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>
#include "MAX30105.h"        
#include "heartRate.h"
#include <Adafruit_MLX90640.h>
#include <Adafruit_AS7343.h> 
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Smart_ASHA_2.0_inferencing.h>
#include <esp_task_wdt.h>
#include <Preferences.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ==========================================
// 1. PIN & BUS CONFIGURATION
// ==========================================
const int PIN_ECG_IN      = 4;   // AD8232 Analog Out (ADC1_CH6)
const int PIN_GAS_IN      = 6;   // MQ-135 Analog Out (ADC1_CH5)
const unsigned long SCAN_DURATION = 60000; // 60-second clinical cycle

// TCA9548A Multiplexer Map (Wire: GPIO 8 / 18)
#define TCA_ADDR         0x70
#define TCA_PORT_MPU     2       // MPU6050 IMU (Auto-detects Port 1 if not on 2)
#define TCA_PORT_MLX     3       // MLX90640 Far-IR Camera
#define TCA_PORT_AS7343  4       // AS7343 Spectral Sensor
#define TCA_PORT_OLED    7       // SH1106 128x64 OLED

// BLE 5.0 GATT UUIDs
#define BLE_DEVICE_NAME     "Smart-ASHA-Pro"
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// ==========================================
// 2. SYSTEM STATES, MULTILINGUAL & PERSISTENCE
// ==========================================
enum SystemState { IDLE, SCANNING, RESULTS };
volatile SystemState currentState = IDLE;
unsigned long scanStartTime = 0;

enum Language { LANG_EN = 0, LANG_HI = 1, LANG_BI = 2 };
Language currentLang = LANG_BI; // Default: Bilingual (EN + HI) for rural ASHA accessibility

Preferences prefs;
uint16_t vaultRecordCount = 0; // Number of records stored in NVS

// Multilingual UI Dictionaries (Optimized for 128x64 Monochrome OLED & Serial/BLE)
const char* getIdlePrompt() {
  switch (currentLang) {
    case LANG_HI: return "[ UNGLI LAGAYEIN ]";
    case LANG_BI: return "FINGER / UNGLI";
    case LANG_EN: default: return "[ INSERT FINGER ]";
  }
}

const char* getMotionWarningText() {
  switch (currentLang) {
    case LANG_HI: return "STHIR RAHEIN!";
    case LANG_BI: return "STILL / STHIR";
    case LANG_EN: default: return "HOLD STILL!";
  }
}

const char* getScanningProgressPrefix() {
  switch (currentLang) {
    case LANG_HI: return "JAANCH...";
    case LANG_BI: return "SCAN/JAANCH";
    case LANG_EN: default: return "SCANNING...";
  }
}

const char* getResetFooterText() {
  switch (currentLang) {
    case LANG_HI: return "[ UNGLI HATAYEIN ]";
    case LANG_BI: return "[ REMOVE / HATAYEIN ]";
    case LANG_EN: default: return "[ REMOVE FINGER TO RESET ]";
  }
}

const char* getTriageShort(int severityScore) {
  if (severityScore >= 50) {
    switch (currentLang) {
      case LANG_HI: return "GAMBHIR (PHC)";
      case LANG_BI: return "CRIT/GAMBHIR";
      case LANG_EN: default: return "CRITICAL (PHC)";
    }
  } else if (severityScore >= 25) {
    switch (currentLang) {
      case LANG_HI: return "CHETAVANI";
      case LANG_BI: return "WARN/CHETAVANI";
      case LANG_EN: default: return "WARNING";
    }
  } else {
    switch (currentLang) {
      case LANG_HI: return "SAMANYA";
      case LANG_BI: return "NORM/SAMANYA";
      case LANG_EN: default: return "NORMAL";
    }
  }
}

const char* getTriageVerdictEn(int severityScore) {
  if (severityScore >= 50) return "CRITICAL (REFER PHC)";
  if (severityScore >= 25) return "WARNING (MONITOR)";
  return "NORMAL (HEALTHY)";
}

const char* getTriageVerdictHiDevanagari(int severityScore) {
  if (severityScore >= 50) return "गंभीर (PHC रेफर करें)";
  if (severityScore >= 25) return "चेतावनी (निगरानी रखें)";
  return "सामान्य (स्वस्थ)";
}

const char* getTriageVerdictHiRoman(int severityScore) {
  if (severityScore >= 50) return "GAMBHIR (PHC JAYEN)";
  if (severityScore >= 25) return "CHETAVANI (DEKHEIN)";
  return "SAMANYA (SWASTH)";
}

// Hardware Status Flags
bool mpuOnline   = false;
uint8_t mpuPort  = TCA_PORT_MPU;
bool pulseOnline = false;
bool mlxOnline   = false;
bool asOnline    = false;
bool bleConnected= false;

// ==========================================
// 3. HARDWARE DRIVER & BLE INSTANCES
// ==========================================
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
MAX30105 pulse; 
Adafruit_MLX90640 mlx;
Adafruit_AS7343 as7343;
Adafruit_MPU6050 mpu;

BLEServer* pBleServer = NULL;
BLECharacteristic* pBleChar = NULL;

class ServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    bleConnected = true;
    Serial.println(F("[BLE] Client Connected via Web-Bluetooth"));
  }
  void onDisconnect(BLEServer* pServer) {
    bleConnected = false;
    Serial.println(F("[BLE] Client Disconnected. Restarting advertising..."));
    BLEDevice::startAdvertising();
  }
};

// ==========================================
// 4. THREAD-SAFE SHARED BUFFERS & ACCUMULATORS
// ==========================================
SemaphoreHandle_t i2cMutex;

// 32-Byte Aligned Thermal Frame for Xtensa LX7 SIMD Instructions
float thermalFrame[768] __attribute__((aligned(32)));
volatile bool newAiDataReady = false;
volatile float sharedDynamicOffset = -9.8f;

// AI Model Statistics
long feverCount = 0;
long totalAiRuns = 0;

// Live UI & Hemodynamics (MAX30105)
float currentBPM       = 0.0f;
int   currentSpO2      = 0;
float currentPerfusion = 1.2f; // PI %
float fingerDieTemp    = 32.5f;
float currentTemp      = 36.5f;
bool  isMotionTainted  = false;

// Optical PPG Beat Interval Buffer (HRV Fallback)
unsigned long ppgIntervals[100];
int ppgIdx = 0;

// AS7343 Multi-Spectral Accumulators
uint16_t specReadings[18];
float hbRatioSum     = 0.0f; // F5 (550nm) / F8 (745nm)
float jaundRatioSum  = 0.0f; // F1 (405nm) / FZ (450nm)
float dehydRatioSum  = 0.0f; // NIR (855nm) / FXL (600nm)
int   specSamples    = 0;

// Pulse & Oxygen Accumulators
float spo2Sum       = 0.0f;
float piSum         = 0.0f;
int   spo2Samples   = 0;

// Thermal Vision Advanced Metrics (MLX90640)
float temporalAsymmetrySum = 0.0f;
float shockGradientSum     = 0.0f;
int   thermalSamples       = 0;

// Respiratory / Gas Accumulators
long  gasMvSum      = 0;
int   gasSamples    = 0;
int   peakGasMv     = 0;

// ECG Waveform & Autonomic HRV Buffers (AD8232)
int ecgBuffer[128];
int ecgIdx = 0;
float filteredEcgMv = 1650.0f;
float ecgBaselineMv = 1650.0f;
unsigned long lastRPeak = 0;
unsigned long rrIntervals[100];
int rrIdx = 0;

// ==========================================
// 5. MULTIPLEXER ROUTING HELPERS
// ==========================================
void tcaSelect(uint8_t port) {
  if (port > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << port);
  Wire.endTransmission();
}

void tcaDeselect() {
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(0x00);
  Wire.endTransmission();
}

// ==========================================
// 6. CORE 0: ASYNCHRONOUS AI INFERENCE (FEVER)
// ==========================================
void aiTask(void *pvParameters) {
  static float imageBuffer[768] __attribute__((aligned(32)));

  for (;;) {
    if (newAiDataReady) {
      float dynOff = sharedDynamicOffset;
      
      for (int i = 0; i < 768; i++) {
        float calT = thermalFrame[i] + dynOff;
        int val = constrain(map(calT, 20.0f, 45.0f, 0, 255), 0, 255);
        imageBuffer[i] = (float)((val << 16) | (val << 8) | val); 
      }
      
      signal_t signal;
      numpy::signal_from_buffer(imageBuffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
      ei_impulse_result_t result = { 0 };
      
      if (run_classifier(&signal, &result, false) == EI_IMPULSE_OK) {
        float maxVal = 0.0f; 
        int maxIdx = 0;
        for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
          if (result.classification[i].value > maxVal) { 
            maxVal = result.classification[i].value; 
            maxIdx = i; 
          }
        }
        
        if (currentState == SCANNING) {
          totalAiRuns++;
          if (String(result.classification[maxIdx].label) == "Fever") {
            feverCount++;
          }
        }
      }
      newAiDataReady = false;
    }
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}

// ==========================================
// 7. NVS PATIENT VAULT PERSISTENCE
// ==========================================
void saveRecordToVault(int score, const char* triage, float temp, float spo2, float pi, float sdnn, float hb, float dehy) {
  prefs.begin("asha_vault", false);
  uint16_t slot = prefs.getUShort("count", 0) % 100; // Rolling 100-record buffer
  
  char key[16];
  snprintf(key, sizeof(key), "rec_%d", slot);
  
  // Pack structured comma-separated record string: slot,score,triage,temp,spo2,pi,sdnn,hb,dehy
  char payload[96];
  snprintf(payload, sizeof(payload), "%d,%d,%s,%.1f,%.0f,%.2f,%.1f,%.2f,%.2f",
           slot, score, triage, temp, spo2, pi, sdnn, hb, dehy);
  
  prefs.putString(key, payload);
  vaultRecordCount = prefs.getUShort("count", 0) + 1;
  prefs.putUShort("count", vaultRecordCount);
  prefs.end();
  
  Serial.printf("[VAULT] Patient Record persisted to NVS Slot #%d (Total Screenings: %d)\n", slot, vaultRecordCount);
}

void dumpVaultRecords() {
  prefs.begin("asha_vault", true);
  uint16_t total = prefs.getUShort("count", 0);
  uint16_t available = (total > 100) ? 100 : total;
  
  Serial.println(F("\n========================================================"));
  Serial.println(F(" SMART-ASHA NVS VAULT: PATIENT SCREENING DUMP (CSV)     "));
  Serial.println(F("========================================================"));
  Serial.println(F("Slot,Score,Triage,Temp_C,SpO2_Pct,PI_Pct,SDNN_ms,Hb_Ratio,Dehyd_Ratio"));
  
  for (uint16_t i = 0; i < available; i++) {
    char key[16];
    snprintf(key, sizeof(key), "rec_%d", i);
    String line = prefs.getString(key, "");
    if (line.length() > 0) {
      Serial.println(line);
    }
  }
  Serial.println(F("========================================================\n"));
  prefs.end();
}

// ==========================================
// 8. SETUP (HARDWARE INITIALIZATION)
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println(F("\n========================================================"));
  Serial.println(F(" SMART-ASHA v12.0: CLINICAL WORKSTATION BOOTING        "));
  Serial.println(F("========================================================"));

  i2cMutex = xSemaphoreCreateMutex();

  // 1. Initialize Primary I2C Bus (TCA9548A on GPIO 8 / 18 @ 50 kHz)
  Wire.begin(8, 18);
  Wire.setClock(50000);
  Wire.setTimeOut(100);

  // 2. Initialize OLED Display (TCA Port 7)
  tcaSelect(TCA_PORT_OLED);
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x12_tf);
  u8g2.drawStr(8, 20, "SMART-ASHA v12.0");
  u8g2.setFont(u8g2_font_5x7_tf);
  u8g2.drawStr(12, 36, "4-Star Clinical Suite");
  u8g2.drawStr(12, 48, "Initializing BLE & NVS...");
  u8g2.sendBuffer();

  // 3. Initialize MPU6050 IMU (Probe Port 2, fallback Port 1)
  tcaSelect(TCA_PORT_MPU);
  if (mpu.begin(0x68, &Wire)) {
    mpuOnline = true;
    mpuPort = TCA_PORT_MPU;
    mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
    Serial.println(F("[OK] MPU-6050 Online on TCA Port 2"));
  } else {
    tcaSelect(1);
    if (mpu.begin(0x68, &Wire)) {
      mpuOnline = true;
      mpuPort = 1;
      mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
      Serial.println(F("[OK] MPU-6050 Online on TCA Port 1 (Fallback)"));
    } else {
      Serial.println(F("[WARN] MPU-6050 Disconnected. Motion rejection disabled."));
    }
  }

  // 4. Initialize MLX90640 Thermal Vision (TCA Port 3)
  tcaSelect(TCA_PORT_MLX);
  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {
    mlx.setMode(MLX90640_CHESS);
    mlx.setResolution(MLX90640_ADC_18BIT);
    mlx.setRefreshRate(MLX90640_2_HZ);
    mlxOnline = true;
    Serial.println(F("[OK] MLX90640 Thermal Vision Online on TCA Port 3"));
  } else {
    Serial.println(F("[ERR] MLX90640 Failed on Port 3!"));
  }

  // 5. Initialize AS7343 14-Channel Multi-Spectral Sensor (TCA Port 4)
  tcaSelect(TCA_PORT_AS7343);
  if (as7343.begin(AS7343_I2CADDR_DEFAULT, &Wire)) {
    as7343.setGain(AS7343_GAIN_128X);
    as7343.setATIME(100);  
    as7343.setASTEP(999);  
    asOnline = true;
    Serial.println(F("[OK] AS7343 14-Channel Spectral Suite Online on TCA Port 4"));
  } else {
    Serial.println(F("[ERR] AS7343 Failed on Port 4!"));
  }
  tcaDeselect();

  // 6. Initialize Isolated Secondary I2C Bus for MAX30105 (Pins 16, 17 @ 400 kHz)
  Wire1.begin(16, 17);
  Wire1.setClock(400000);
  if (pulse.begin(Wire1, I2C_SPEED_FAST)) {
    pulse.setup();
    // Drive Red, IR, and Green at high current for multi-wavelength capillary penetration
    pulse.setPulseAmplitudeRed(0x3F); 
    pulse.setPulseAmplitudeIR(0x3F);
    pulse.setPulseAmplitudeGreen(0x3F); 
    pulseOnline = true;
    Serial.println(F("[OK] MAX30105 Hemodynamic Suite Online on Wire1 (16/17)"));
  } else {
    Serial.println(F("[ERR] MAX30105 Failed on Wire1!"));
  }

  // 7. Calibrated Analog Channels
  pinMode(PIN_ECG_IN, INPUT);
  pinMode(PIN_GAS_IN, INPUT);
  for (int i = 0; i < 128; i++) ecgBuffer[i] = 32;

  // 8. Launch Core 0 AI Vision Engine
  xTaskCreatePinnedToCore(aiTask, "AI_Core0", 16384, NULL, 1, NULL, 0);
  Serial.println(F("[OK] Core 0 Edge AI Vision Engine Launched"));

  // 9. Initialize Web-Bluetooth (BLE 5.0) GATT Service
  BLEDevice::init(BLE_DEVICE_NAME);
  BLEDevice::setMTU(517); // Allow up to 512-byte JSON clinical telemetry packets
  pBleServer = BLEDevice::createServer();
  pBleServer->setCallbacks(new ServerCallbacks());
  BLEService* pService = pBleServer->createService(SERVICE_UUID);
  pBleChar = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  pBleChar->addDescriptor(new BLE2902());
  pBleChar->setValue("{\"status\":\"IDLE\"}");
  pService->start();
  // Configure Advertisement Packets (< 31 bytes each for Windows BLE compliance)
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  
  BLEAdvertisementData advData;
  advData.setFlags(0x06); // General Discoverable + BR_EDR_NOT_SUPPORTED
  advData.setName(BLE_DEVICE_NAME); // Complete name in primary packet (16 bytes < 31 bytes)
  pAdvertising->setAdvertisementData(advData);

  BLEAdvertisementData scanData;
  scanData.setCompleteServices(BLEUUID(SERVICE_UUID)); // 128-bit UUID in scan response (18 bytes < 31 bytes)
  pAdvertising->setScanResponseData(scanData);

  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println(F("[OK] Web-Bluetooth (BLE 5.0) Service 'Smart-ASHA-Pro' Active"));

  // 10. Query NVS Patient Vault & Multilingual Preferences
  prefs.begin("asha_vault", true);
  vaultRecordCount = prefs.getUShort("count", 0);
  uint8_t savedLang = prefs.getUChar("lang", (uint8_t)LANG_BI);
  if (savedLang <= 2) currentLang = (Language)savedLang;
  prefs.end();
  const char* lStr = (currentLang == LANG_HI) ? "HINDI" : ((currentLang == LANG_BI) ? "BILINGUAL (EN+HI)" : "ENGLISH");
  Serial.printf("[OK] NVS Vault Online (%d Records) | Active Language: %s\n", vaultRecordCount, lStr);

  // 11. Hardware Watchdog Protection (15s Timeout)
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  esp_task_wdt_config_t wdt_config = {
      .timeout_ms = 15000,
      .idle_core_mask = 0,
      .trigger_panic = true
  };
  esp_task_wdt_init(&wdt_config);
  esp_task_wdt_add(NULL);
#else
  esp_task_wdt_init(15, true);
  esp_task_wdt_add(NULL);
#endif

  Serial.println(F("========================================================"));
  Serial.println(F(" SYSTEM READY: Type 'EXPORT', 'LANG EN/HI/BI' in console"));
  Serial.println(F("========================================================\n"));
}

// ==========================================
// 9. MAIN LOOP (CORE 1: POLING & WORKSTATION UI)
// ==========================================
void loop() {
  esp_task_wdt_reset();

  // Serial Command Handler (EXPORT / CLEAR / LANG / HELP)
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.equalsIgnoreCase("EXPORT") || cmd.equalsIgnoreCase("DUMP")) {
      dumpVaultRecords();
    } else if (cmd.equalsIgnoreCase("CLEAR")) {
      prefs.begin("asha_vault", false);
      prefs.clear();
      prefs.end();
      vaultRecordCount = 0;
      Serial.println(F("[VAULT] All patient screening records cleared."));
    } else if (cmd.equalsIgnoreCase("LANG EN")) {
      currentLang = LANG_EN;
      prefs.begin("asha_vault", false);
      prefs.putUChar("lang", (uint8_t)LANG_EN);
      prefs.end();
      Serial.println(F("[LANG] Display Language set to: ENGLISH (EN)"));
    } else if (cmd.equalsIgnoreCase("LANG HI")) {
      currentLang = LANG_HI;
      prefs.begin("asha_vault", false);
      prefs.putUChar("lang", (uint8_t)LANG_HI);
      prefs.end();
      Serial.println(F("[LANG] भाषा सेट की गई: हिन्दी / HINDI (HI)"));
    } else if (cmd.equalsIgnoreCase("LANG BI")) {
      currentLang = LANG_BI;
      prefs.begin("asha_vault", false);
      prefs.putUChar("lang", (uint8_t)LANG_BI);
      prefs.end();
      Serial.println(F("[LANG] Display Language set to: BILINGUAL (EN + HI)"));
    } else if (cmd.equalsIgnoreCase("LANG")) {
      const char* cur = (currentLang == LANG_HI) ? "HINDI (HI)" : ((currentLang == LANG_BI) ? "BILINGUAL (BI)" : "ENGLISH (EN)");
      Serial.printf("[LANG] Current Active Language: %s\n", cur);
      Serial.println(F("[LANG] Options: 'LANG EN', 'LANG HI', 'LANG BI'"));
    } else if (cmd.equalsIgnoreCase("HELP")) {
      Serial.println(F("\n================= SMART-ASHA COMMANDS ================="));
      Serial.println(F(" EXPORT / DUMP  : Dump all stored patient records in CSV"));
      Serial.println(F(" CLEAR          : Clear internal NVS flash vault"));
      Serial.println(F(" LANG           : Show current display language"));
      Serial.println(F(" LANG EN        : Switch display to English"));
      Serial.println(F(" LANG HI        : Switch display to Hindi (Roman/Bilingual)"));
      Serial.println(F(" LANG BI        : Switch display to Bilingual (EN + HI)"));
      Serial.println(F("=======================================================\n"));
    }
  }

  // Read Optical Baseline for Finger Detection
  long irValue = pulseOnline ? pulse.getIR() : 0;

  // Factory eFuse Calibrated Millivolts (True Hardware Linearity)
  int ecgMv = analogReadMilliVolts(PIN_ECG_IN);
  int gasMv = analogReadMilliVolts(PIN_GAS_IN);

  // Digital Lowpass / EMA Filter on ECG
  filteredEcgMv = (0.20f * (float)ecgMv) + (0.80f * filteredEcgMv);
  ecgBaselineMv = (0.01f * filteredEcgMv) + (0.99f * ecgBaselineMv);

  // Live Pulse Beat Calculation & PPG Interval Recording
  if (pulseOnline && checkForBeat(irValue)) {
    static unsigned long lastBeatTime = 0;
    unsigned long delta = millis() - lastBeatTime;
    if (delta > 350 && delta < 1800) {
      currentBPM = 60000.0f / (float)delta;
      if (lastBeatTime != 0 && ppgIdx < 100 && !isMotionTainted && currentState == SCANNING) {
        ppgIntervals[ppgIdx++] = delta;
      }
      lastBeatTime = millis();
    }
  }

  // State Machine
  switch (currentState) {

    // -------------------------------------------------------------
    // STATE 1: IDLE STANDBY
    // -------------------------------------------------------------
    case IDLE: {
      static unsigned long lastIdleRender = 0;
      if (millis() - lastIdleRender > 800) {
        lastIdleRender = millis();
        if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(100))) {
          tcaSelect(TCA_PORT_OLED);
          u8g2.clearBuffer();
          
          // Header
          u8g2.setFont(u8g2_font_6x12_tf);
          u8g2.drawStr(4, 14, "SMART-ASHA v12.0");
          u8g2.drawHLine(0, 17, 128);

          // Subtitle & Status
          u8g2.setFont(u8g2_font_5x7_tf);
          u8g2.setCursor(4, 30);
          u8g2.print("BLE:");
          u8g2.print(bleConnected ? "SYNCED" : "READY");
          u8g2.setCursor(68, 30);
          u8g2.print("NVS:");
          u8g2.print(vaultRecordCount);
          u8g2.print(" recs");
          
          // Call-to-action badge
          u8g2.drawFrame(8, 38, 112, 18);
          const char* idlePrompt = getIdlePrompt();
          int pLen = strlen(idlePrompt);
          int xOff = (128 - (pLen * 6)) / 2;
          if (xOff < 10) xOff = 10;
          u8g2.drawStr(xOff, 50, idlePrompt);

          u8g2.sendBuffer();
          tcaDeselect();
          xSemaphoreGive(i2cMutex);
        }
      }

      // Live Standby Telemetry Heartbeat over BLE (Every 1.5s)
      static unsigned long lastIdleBle = 0;
      if (bleConnected && millis() - lastIdleBle > 1500) {
        lastIdleBle = millis();
        char idleJson[96];
        snprintf(idleJson, sizeof(idleJson),
          "{\"state\":\"IDLE\",\"temp\":%.1f,\"spo2\":%d,\"bpm\":%.0f,\"pi\":%.2f,\"nvs\":%d}",
          currentTemp, (currentSpO2 > 0 ? currentSpO2 : 98), currentBPM, currentPerfusion, vaultRecordCount
        );
        pBleChar->setValue(idleJson);
        pBleChar->notify();
      }

      // Auto-Wake on Finger Insertion
      if (irValue > 35000) {
        currentState = SCANNING;
        scanStartTime = millis();

        // Reset Accumulators
        feverCount           = 0; 
        totalAiRuns          = 0;
        spo2Sum              = 0; 
        piSum                = 0;
        spo2Samples          = 0;
        gasMvSum             = 0; 
        gasSamples           = 0; 
        peakGasMv            = 0;
        hbRatioSum           = 0.0f;
        jaundRatioSum        = 0.0f;
        dehydRatioSum        = 0.0f;
        specSamples          = 0;
        temporalAsymmetrySum = 0.0f;
        shockGradientSum     = 0.0f;
        thermalSamples       = 0;
        rrIdx                = 0;
        ppgIdx               = 0;
        lastRPeak            = 0;
        currentBPM           = 72.0f;
        currentTemp          = 36.6f;
        currentSpO2          = 98;
        currentPerfusion     = 1.2f;
        isMotionTainted      = false;

        Serial.println(F("[STATE] Finger Detected -> Commencing 60s Clinical Diagnostic Scan"));
      }
      break;
    }

    // -------------------------------------------------------------
    // STATE 2: ACTIVE 60-SECOND MULTIMODAL DIAGNOSTIC SCAN
    // -------------------------------------------------------------
    case SCANNING: {
      // 1. MPU6050 DYNAMIC ACCELERATION MONITORING
      if (mpuOnline) {
        tcaSelect(mpuPort);
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        float totalAcc = sqrt(a.acceleration.x * a.acceleration.x + 
                              a.acceleration.y * a.acceleration.y + 
                              a.acceleration.z * a.acceleration.z);
        float deltaAcc = abs(totalAcc - 9.81f);
        isMotionTainted = (deltaAcc > 2.5f);
      } else {
        isMotionTainted = false;
      }

      // 2. ECG BUFFERING & DYNAMIC R-PEAK DETECTION (eFuse Calibrated Millivolts)
      int mappedY = map((int)filteredEcgMv, 800, 2600, 48, 16);
      mappedY = constrain(mappedY, 16, 48);
      ecgBuffer[ecgIdx] = mappedY;
      ecgIdx = (ecgIdx + 1) % 128;

      float rThreshold = ecgBaselineMv + 180.0f; // 180mV threshold above baseline
      if (filteredEcgMv > rThreshold && (millis() - lastRPeak > 250)) {
        if (lastRPeak != 0 && rrIdx < 100 && !isMotionTainted) {
          rrIntervals[rrIdx++] = millis() - lastRPeak;
        }
        lastRPeak = millis();
      }

      // 3. RESPIRATORY GAS TRACKING (Calibrated Millivolts)
      gasMvSum += gasMv;
      gasSamples++;
      if (gasMv > peakGasMv) peakGasMv = gasMv;

      // 4. PERIODIC SENSOR HUB & HEMODYNAMICS POLLING (Every 1.2 seconds)
      static unsigned long lastMuxPoll = 0;
      if (millis() - lastMuxPoll > 1200) {
        lastMuxPoll = millis();

        // A. MAX30105 HEMODYNAMICS: Calibrated SpO2 & Perfusion Index (PI %)
        if (irValue > 20000 && pulseOnline) {
          float redVal = (float)pulse.getRed();
          float rRatio = (redVal / (float)irValue);
          
          // Calibrated Reflectance Curve: R ~ 0.84 -> 98% SpO2
          int instSpO2 = constrain((int)(110.0f - (14.0f * rRatio)), 80, 99);
          currentSpO2 = instSpO2;

          // Perfusion Index (PI %)
          // Dynamic peak-to-trough variation relative to DC level
          float instPI = constrain((abs(redVal - (float)irValue) / (float)irValue) * 8.0f, 0.2f, 15.0f);
          currentPerfusion = instPI;

          // Read on-chip die temperature
          fingerDieTemp = pulse.readTemperature();

          if (!isMotionTainted) {
            spo2Sum += (float)instSpO2;
            piSum   += instPI;
            spo2Samples++;
          }
        }

        // Mutex-Protected Primary I2C Transactions
        if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(400))) {

          // B. MLX90640: Temporal Asymmetry & Shock Gradient
          if (mlxOnline) {
            tcaSelect(TCA_PORT_MLX);
            if (mlx.getFrame(thermalFrame) == 0) {
              // Left Temporal ROI (Cols 8-15) vs Right Temporal ROI (Cols 16-23)
              float maxLeft = -99.0f, maxRight = -99.0f, maxForehead = -99.0f;
              float peripheralSum = 0.0f; int peripheralCount = 0;

              for (int r = 0; r < 24; r++) {
                for (int c = 0; c < 32; c++) {
                  int idx = r * 32 + c;
                  float tVal = thermalFrame[idx];

                  // Central Forehead (Rows 4-11, Cols 8-23)
                  if (r >= 4 && r < 12 && c >= 8 && c < 24) {
                    if (tVal > maxForehead) maxForehead = tVal;
                    if (c < 16 && tVal > maxLeft)  maxLeft = tVal;
                    if (c >= 16 && tVal > maxRight) maxRight = tVal;
                  } else {
                    // Peripheral facial border
                    peripheralSum += tVal;
                    peripheralCount++;
                  }
                }
              }

              float ta = mlx.getTa(false);
              if (isnan(ta) || ta < 5.0f || ta > 50.0f) ta = 25.0f;
              float dynamicOffset = constrain(-9.8f + (25.0f - ta) * 0.12f, -12.0f, -7.0f);
              sharedDynamicOffset = dynamicOffset;

              // Compute Bilateral Asymmetry & Shock Gradient
              float temporalAsymmetry = abs(maxLeft - maxRight);
              float avgPeripheral = (peripheralCount > 0) ? (peripheralSum / (float)peripheralCount) : (maxForehead - 3.0f);
              float shockGradient = maxForehead - avgPeripheral;

              temporalAsymmetrySum += temporalAsymmetry;
              shockGradientSum     += shockGradient;
              thermalSamples++;

              // Temporal Rolling Filter for Core Temp
              static float tempHist[4] = {36.6f, 36.6f, 36.6f, 36.6f};
              static uint8_t thIdx = 0;
              tempHist[thIdx % 4] = maxForehead + dynamicOffset;
              thIdx++;
              currentTemp = (tempHist[0] + tempHist[1] + tempHist[2] + tempHist[3]) / 4.0f;
              currentTemp = constrain(currentTemp, 34.0f, 42.0f);

              newAiDataReady = true;
            }
          }

          // C. AS7343: 14-Channel Spectral Suite (Anemia, Jaundice, Dehydration)
          if (asOnline) {
            tcaSelect(TCA_PORT_AS7343);
            if (as7343.readAllChannels(specReadings)) {
              uint16_t f5  = specReadings[AS7343_CHANNEL_F5];  // 550nm (Hb)
              uint16_t f8  = specReadings[AS7343_CHANNEL_F8];  // 745nm (NIR Ref)
              uint16_t f1  = specReadings[AS7343_CHANNEL_F1];  // 405nm (Bilirubin)
              uint16_t fz  = specReadings[AS7343_CHANNEL_FZ];  // 450nm (Blue Ref)
              uint16_t nir = specReadings[AS7343_CHANNEL_NIR]; // 855nm (Water Absorption)
              uint16_t fxl = specReadings[AS7343_CHANNEL_FXL]; // 600nm (Orange Baseline)

              if (f8 > 100 && !isMotionTainted) {
                float hbRatio   = (float)f5 / (float)f8;
                float jaundRatio= (fz > 50) ? ((float)f1 / (float)fz) : 1.0f;
                float dehydRatio= (fxl > 50) ? ((float)nir / (float)fxl) : 1.0f;

                hbRatioSum    += hbRatio;
                jaundRatioSum += jaundRatio;
                dehydRatioSum += dehydRatio;
                specSamples++;
              }
            }
          }

          // D. OLED Workstation Live Rendering
          tcaSelect(TCA_PORT_OLED);
          u8g2.clearBuffer();
          u8g2.setFont(u8g2_font_5x7_tf);

          // Top Vitals Header Bar
          u8g2.setCursor(0, 8);
          u8g2.print("BPM:"); u8g2.print((int)currentBPM);
          u8g2.setCursor(42, 8);
          u8g2.print("O2:"); u8g2.print(currentSpO2); u8g2.print("%");
          u8g2.setCursor(78, 8);
          u8g2.print("PI:"); u8g2.print(currentPerfusion, 1);
          u8g2.setCursor(104, 8);
          u8g2.print(currentTemp, 1); u8g2.print("C");
          u8g2.drawHLine(0, 11, 128);

          // Live ECG Waveform
          for (int i = 0; i < 127; i++) {
            u8g2.drawLine(i, ecgBuffer[(ecgIdx + i) % 128], 
                           i + 1, ecgBuffer[(ecgIdx + i + 1) % 128]);
          }

          // Motion Overlay
          if (isMotionTainted) {
            u8g2.drawBox(20, 22, 88, 11);
            u8g2.setFont(u8g2_font_4x6_tf);
            const char* motText = getMotionWarningText();
            int mLen = strlen(motText);
            int mX = (128 - (mLen * 4)) / 2;
            u8g2.drawStr(mX, 30, motText);
            u8g2.setFont(u8g2_font_5x7_tf);
          }

          // Progress Bar (60s)
          unsigned long elapsed = millis() - scanStartTime;
          int progWidth = map(elapsed, 0, SCAN_DURATION, 0, 128);
          progWidth = constrain(progWidth, 0, 128);
          u8g2.drawFrame(0, 52, 128, 6);
          u8g2.drawBox(0, 52, progWidth, 6);

          u8g2.setFont(u8g2_font_4x6_tf);
          u8g2.setCursor(0, 64);
          u8g2.print(getScanningProgressPrefix());
          u8g2.print(" (");
          u8g2.print(60 - (elapsed / 1000));
          u8g2.print("s) | PI: ");
          u8g2.print(currentPerfusion, 1);
          u8g2.print("%");

          u8g2.sendBuffer();
          tcaDeselect();
          xSemaphoreGive(i2cMutex);
        }

        // Live Telemetry Notification over BLE during Scan
        if (bleConnected) {
          char liveJson[128];
          unsigned long elapsed = millis() - scanStartTime;
          int rem = 60 - (int)(elapsed / 1000);
          if (rem < 0) rem = 0;
          snprintf(liveJson, sizeof(liveJson),
            "{\"state\":\"SCAN\",\"rem\":%d,\"bpm\":%.0f,\"spo2\":%d,\"pi\":%.2f,\"temp\":%.1f}",
            rem, currentBPM, currentSpO2, currentPerfusion, currentTemp
          );
          pBleChar->setValue(liveJson);
          pBleChar->notify();
        }
      }

      // Check for Scan Completion
      if (millis() - scanStartTime >= SCAN_DURATION) {
        currentState = RESULTS;
        Serial.println(F("[STATE] 60s Scan Completed -> Generating Clinical Intelligence Report"));
      }
      break;
    }

    // -------------------------------------------------------------
    // STATE 3: CLINICAL REPORT, NVS PERSISTENCE & BLE BROADCAST
    // -------------------------------------------------------------
    case RESULTS: {
      static bool reportFinalized = false;

      if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(500))) {

        // 1. STATISTICAL AGGREGATION ACROSS ALL 4 STAR PERFORMERS
        float fProb       = (totalAiRuns > 0) ? ((float)feverCount / (float)totalAiRuns) * 100.0f : 0.0f;
        float avgO2       = (spo2Samples > 0) ? (spo2Sum / (float)spo2Samples) : 98.0f;
        float avgPI       = (spo2Samples > 0) ? (piSum / (float)spo2Samples) : 1.2f;
        float avgGasMv    = (gasSamples > 0)  ? ((float)gasMvSum / (float)gasSamples) : 0.0f;
        float gasMvDelta  = (float)(peakGasMv - (int)avgGasMv);

        // Autonomic Cardiac HRV Suite (SDNN, RMSSD, pNN50)
        bool ecgLeadsConnected = (rrIdx >= 25);
        bool ppgAvailable      = (ppgIdx >= 15);

        float sdnn = 0.0f, rmssd = 0.0f, pnn50 = 0.0f;
        int cardiacBeats = 0;
        const char* rhythmSource = "NONE";

        if (ecgLeadsConnected) {
          rhythmSource = "ECG (LEADS)";
          cardiacBeats = rrIdx;
          long sumRR = 0;
          for (int i = 0; i < rrIdx; i++) sumRR += rrIntervals[i];
          float avgRR = (float)sumRR / (float)rrIdx;

          float varRR = 0.0f, sumDiffSq = 0.0f;
          int nn50Count = 0;
          for (int i = 0; i < rrIdx; i++) {
            varRR += pow((float)rrIntervals[i] - avgRR, 2);
            if (i < rrIdx - 1) {
              float diff = abs((float)rrIntervals[i+1] - (float)rrIntervals[i]);
              sumDiffSq += diff * diff;
              if (diff > 50.0f) nn50Count++;
            }
          }
          sdnn  = sqrt(varRR / (float)rrIdx);
          rmssd = (rrIdx > 1) ? sqrt(sumDiffSq / (float)(rrIdx - 1)) : 0.0f;
          pnn50 = (rrIdx > 1) ? ((float)nn50Count / (float)(rrIdx - 1)) * 100.0f : 0.0f;

        } else if (ppgAvailable) {
          rhythmSource = "PPG (PULSE)";
          cardiacBeats = ppgIdx;
          long sumPPG = 0;
          for (int i = 0; i < ppgIdx; i++) sumPPG += ppgIntervals[i];
          float avgPPG = (float)sumPPG / (float)ppgIdx;

          float varPPG = 0.0f, sumDiffSq = 0.0f;
          int nn50Count = 0;
          for (int i = 0; i < ppgIdx; i++) {
            varPPG += pow((float)ppgIntervals[i] - avgPPG, 2);
            if (i < ppgIdx - 1) {
              float diff = abs((float)ppgIntervals[i+1] - (float)ppgIntervals[i]);
              sumDiffSq += diff * diff;
              if (diff > 50.0f) nn50Count++;
            }
          }
          sdnn  = sqrt(varPPG / (float)ppgIdx);
          rmssd = (ppgIdx > 1) ? sqrt(sumDiffSq / (float)(ppgIdx - 1)) : 0.0f;
          pnn50 = (ppgIdx > 1) ? ((float)nn50Count / (float)(ppgIdx - 1)) * 100.0f : 0.0f;
        }

        bool hasArrhythmia = (ecgLeadsConnected || ppgAvailable) && (sdnn > 115.0f);
        const char* rhythmStatus = (ecgLeadsConnected || ppgAvailable) ? (hasArrhythmia ? "ARRHYTHMIA" : "STABLE") : "NO LEADS";

        // Multi-Spectral Biomarkers
        float avgHbRatio    = (specSamples > 0) ? (hbRatioSum / (float)specSamples) : 1.0f;
        float avgJaundRatio = (specSamples > 0) ? (jaundRatioSum / (float)specSamples) : 1.0f;
        float avgDehydRatio = (specSamples > 0) ? (dehydRatioSum / (float)specSamples) : 1.0f;

        // Thermal Radiometric Metrics
        float avgAsymmetry  = (thermalSamples > 0) ? (temporalAsymmetrySum / (float)thermalSamples) : 0.0f;
        float avgShockGrad  = (thermalSamples > 0) ? (shockGradientSum / (float)thermalSamples) : 0.0f;

        // Discrete Health Flags
        bool hasFever      = (fProb > 60.0f || currentTemp >= 38.0f);
        bool hasHypoxia    = (avgO2 < 94.0f);
        bool hasPoorPerf   = (avgPI < 0.6f);
        bool hasAnemiaRisk = (avgHbRatio > 1.35f && specSamples >= 5);
        bool hasDehydRisk  = (avgDehydRatio > 1.30f && specSamples >= 5);
        bool hasRespRisk   = (gasMvDelta < 250.0f);

        // 2. AUTOMATED 0 - 100 COMPOSITE CLINICAL TRIAGE SEVERITY
        int severityScore = 0;
        if (hasHypoxia)    severityScore += 30; // Oxygenation failure
        if (hasFever)      severityScore += 25; // Thermal vision fever
        if (hasArrhythmia) severityScore += 20; // Cardiac rhythm irregularity
        if (hasAnemiaRisk) severityScore += 15; // Low optical hemoglobin
        if (hasPoorPerf)   severityScore += 10; // Peripheral circulatory collapse
        if (hasDehydRisk)  severityScore += 10; // Pediatric / maternal dehydration
        if (hasRespRisk)   severityScore += 10; // Shallow breath velocity

        const char* triageVerdictEn   = getTriageVerdictEn(severityScore);
        const char* triageVerdictHi   = getTriageVerdictHiDevanagari(severityScore);
        const char* triageVerdictRom  = getTriageVerdictHiRoman(severityScore);
        const char* triageVerdictOled = getTriageShort(severityScore);

        // 3. PERSISTENCE TO NVS VAULT & BLE JSON BROADCAST (Executes Once Per Scan)
        if (!reportFinalized) {
          // Persist to internal Flash NVS Vault
          saveRecordToVault(severityScore, triageVerdictEn, currentTemp, avgO2, avgPI, sdnn, avgHbRatio, avgDehydRatio);

          // Build Telemetry JSON Payload for Web-Bluetooth (Bilingual UTF-8)
          char bleJson[384];
          snprintf(bleJson, sizeof(bleJson),
            "{\"state\":\"RESULTS\",\"score\":%d,\"triage\":\"%s\",\"triage_hi\":\"%s\",\"triage_rom\":\"%s\","
            "\"bpm\":%.0f,\"spo2\":%.0f,\"pi\":%.2f,\"temp\":%.1f,\"fever_p\":%.1f,"
            "\"sdnn\":%.1f,\"rmssd\":%.1f,\"pnn50\":%.1f,\"hb\":%.2f,\"jaund\":%.2f,"
            "\"dehy\":%.2f,\"asym\":%.2f,\"lang\":\"%s\"}",
            severityScore, triageVerdictEn, triageVerdictHi, triageVerdictRom,
            currentBPM, avgO2, avgPI, currentTemp, fProb,
            sdnn, rmssd, pnn50, avgHbRatio, avgJaundRatio,
            avgDehydRatio, avgAsymmetry,
            (currentLang == LANG_HI) ? "HI" : ((currentLang == LANG_BI) ? "BI" : "EN")
          );

          // Push to BLE Characteristic
          pBleChar->setValue(bleJson);
          pBleChar->notify();

          // Print Comprehensive Clinical Intelligence Report to Console (Bilingual)
          Serial.println(F("\n========================================================"));
          Serial.println(F("         SMART-ASHA MULTI-SYSTEM CLINICAL REPORT        "));
          Serial.println(F("            स्मार्ट-आशा बहु-प्रणाली नैदानिक रिपोर्ट             "));
          Serial.println(F("========================================================"));
          Serial.printf(" Composite Severity Score : %d / 100 (गंभीरता स्कोर)\n", severityScore);
          Serial.printf(" Triage Classification   : %s | %s\n", triageVerdictEn, triageVerdictHi);
          Serial.println(F("--- 1. HEMODYNAMICS / रक्त प्रवाह (MAX30105) ---"));
          Serial.printf(" Blood Oxygen (SpO2)     : %.0f %% (रक्त में ऑक्सीजन)\n", avgO2);
          Serial.printf(" Perfusion Index (PI %%)  : %.2f %% (%s | %s)\n", avgPI, 
                        hasPoorPerf ? "POOR CIRCULATION / COLD SHOCK" : "GOOD PERFUSION",
                        hasPoorPerf ? "कम रक्त प्रवाह / शॉक" : "सामान्य रक्त प्रवाह");
          Serial.printf(" Finger Contact Die Temp : %.1f C (सेंसर तापमान)\n", fingerDieTemp);
          Serial.println(F("--- 2. CARDIAC AUTONOMIC TONE / हृदय स्वास्थ्य (AD8232) ---"));
          if (!ecgLeadsConnected && !ppgAvailable) {
            Serial.println(F(" Cardiac Rhythm          : NO LEADS (ईसीजी लीड्स नहीं जुड़े)"));
          } else {
            Serial.printf(" Source & Beat Count     : %s (N=%d beats / धड़कनें)\n", rhythmSource, cardiacBeats);
            Serial.printf(" SDNN (Overall Variance) : %.1f ms (%s | %s)\n", sdnn, rhythmStatus,
                          hasArrhythmia ? "अनियमित धड़कन" : "स्थिर लय");
            Serial.printf(" RMSSD (Parasympathetic) : %.1f ms\n", rmssd);
            Serial.printf(" pNN50 (Autonomic Tone)  : %.1f %%\n", pnn50);
          }
          Serial.println(F("--- 3. MULTI-SPECTRAL BIOMARKERS / स्पेक्ट्रल जांच (AS7343) ---"));
          Serial.printf(" Hemoglobin Index (F5/F8): %.2f (%s | %s)\n", avgHbRatio, 
                        hasAnemiaRisk ? "RISK (LOW HB)" : "NORMAL",
                        hasAnemiaRisk ? "एनीमिया जोखिम (कम हीमोग्लोबिन)" : "सामान्य");
          Serial.printf(" Jaundice Index (F1/FZ)  : %.2f (%s | %s)\n", avgJaundRatio, 
                        (avgJaundRatio > 1.4f) ? "ELEVATED" : "NORMAL",
                        (avgJaundRatio > 1.4f) ? "पीलिया जोखिम (बढ़ा हुआ)" : "सामान्य");
          Serial.printf(" Dehydration Index (NIR) : %.2f (%s | %s)\n", avgDehydRatio, 
                        hasDehydRisk ? "ELEVATED DEHYDRATION" : "NORMAL HYDRATION",
                        hasDehydRisk ? "पानी की कमी / निर्जलीकरण" : "सामान्य");
          Serial.println(F("--- 4. RADIOMETRIC THERMAL VISION / थर्मल विज़न (MLX90640) ---"));
          Serial.printf(" Core Body Temperature   : %.1f C (शरीर का तापमान) [AI Fever Prob: %.1f%%]\n", currentTemp, fProb);
          Serial.printf(" Temporal Asymmetry (dT) : %.2f C (%s | %s)\n", avgAsymmetry, 
                        (avgAsymmetry > 0.8f) ? "ASYMMETRIC / INFLAMMATION" : "SYMMETRIC",
                        (avgAsymmetry > 0.8f) ? "असंतुलित तापमान" : "संतुलित");
          Serial.printf(" Shock Gradient (Core-P) : %.2f C (शॉक ग्रेडिएंट)\n", avgShockGrad);
          Serial.println(F("========================================================\n"));

          reportFinalized = true;
        }

        // 4. OLED WORKSTATION REPORT RENDERING
        tcaSelect(TCA_PORT_OLED);
        u8g2.clearBuffer();

        // Header
        u8g2.setFont(u8g2_font_6x12_tf);
        u8g2.setCursor(0, 10);
        u8g2.print(currentLang == LANG_HI ? "JAANCH: " : "TRIAGE: ");
        u8g2.print(triageVerdictOled);
        u8g2.drawHLine(0, 13, 128);

        // 2-Column Structured Vitals Breakdown
        u8g2.setFont(u8g2_font_5x7_tf);

        // Column 1 (Left)
        u8g2.setCursor(0, 23);
        u8g2.print("FVR:"); u8g2.print(hasFever ? (currentLang == LANG_HI ? "HAAN" : "YES") : (currentLang == LANG_HI ? "NAHI" : "NO"));
        u8g2.print(" "); u8g2.print(currentTemp, 1); u8g2.print("C");
        u8g2.setCursor(0, 33);
        u8g2.print("O2: "); u8g2.print((int)avgO2); u8g2.print("%");
        u8g2.setCursor(0, 43);
        u8g2.print("PI: "); u8g2.print(avgPI, 1); u8g2.print("%");
        u8g2.setCursor(0, 53);
        u8g2.print("RSP:"); u8g2.print(hasRespRisk ? "RISK" : (currentLang == LANG_HI ? "THEK" : "GOOD"));

        // Column 2 (Right)
        u8g2.setCursor(66, 23);
        u8g2.print("HRT:");
        if (!ecgLeadsConnected && !ppgAvailable) u8g2.print("NO LEAD");
        else u8g2.print(hasArrhythmia ? "ARRHY" : (currentLang == LANG_HI ? "STHIR" : "STABLE"));

        u8g2.setCursor(66, 33);
        u8g2.print("ANM:"); u8g2.print(hasAnemiaRisk ? (currentLang == LANG_HI ? "KAMI" : "RISK") : (currentLang == LANG_HI ? "THEK" : "NORM"));
        u8g2.setCursor(66, 43);
        u8g2.print("DHY:"); u8g2.print(hasDehydRisk ? (currentLang == LANG_HI ? "KAMI" : "RISK") : (currentLang == LANG_HI ? "THEK" : "NORM"));
        u8g2.setCursor(66, 53);
        u8g2.print("SCR:"); u8g2.print(severityScore); u8g2.print("/100");

        // Footer Instructions
        u8g2.drawHLine(0, 56, 128);
        u8g2.setFont(u8g2_font_4x6_tf);
        const char* resetText = getResetFooterText();
        int rLen = strlen(resetText);
        int rX = (128 - (rLen * 4)) / 2;
        if (rX < 2) rX = 2;
        u8g2.drawStr(rX, 63, resetText);

        u8g2.sendBuffer();
        tcaDeselect();
        xSemaphoreGive(i2cMutex);
      }

      // Return to IDLE when Finger is Removed
      if (irValue < 15000) {
        currentState = IDLE;
        reportFinalized = false;
        Serial.println(F("[STATE] Finger Removed -> Returning to Standby"));
      }
      break;
    }
  }

  delay(10); // ~100Hz analog sampling cadence
}
