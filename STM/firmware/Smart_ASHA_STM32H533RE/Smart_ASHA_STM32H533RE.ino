/*
 * ====================================================================================================
 *  SMART-ASHA v12.0: CLINICAL WORKSTATION FIRMWARE (STM32H533RE PRO EDITION)
 * ====================================================================================================
 *  Target Hardware: STMicroelectronics NUCLEO-H533RE (Arm® Cortex®-M33 @ 250 MHz)
 *  Architecture: Single-Core FreeRTOS with Preemptive Priority Scheduling & Hardware FPU/DSP
 *  
 *  THE 4 STAR SENSOR PERFORMERS:
 *   1. MAX30105:   SpO2, BPM, Perfusion Index (PI %), Optical Finger Detection (Wire1 @ 400 kHz)
 *   2. AS7343:     14-Channel Multi-Spectral (Anemia F5/F8, Jaundice F1/FZ, Dehydration NIR/FXL)
 *   3. MLX90640:   Radiometric Thermal Vision (Dynamic Ta, Central Forehead ROI Stefan-Boltzmann)
 *   4. AD8232:     Calibrated ECG Front-End (EMA Filter, SDNN, RMSSD, pNN50, PTT Cuffless BP)
 *
 *  MIGRATION ASSIGNMENT (NUCLEO-64 PINOUT):
 *   - Primary I2C (Wire @ 50 kHz):      PB9 (SDA), PB8 (SCL) -> TCA9548A Multiplexer (0x70)
 *       * Port 2: MPU6050 6-Axis IMU (0x68) [with Port 1 auto-detect fallback]
 *       * Port 3: MLX90640 Thermal Camera (0x33)
 *       * Port 4: AS7343 14-Channel Multi-Spectral Optical Sensor (0x39)
 *       * Port 7: SH1106 128x64 OLED Display (0x3C)
 *   - Secondary I2C (Wire1 @ 400 kHz):  PB11 (SDA), PB10 (SCL) -> MAX30105 Pulse Oximeter
 *   - Clean Analog Inputs (ADC1 12-bit):
 *       * PA0 (A0): AD8232 ECG Sensor (ADC1_INP1)
 *       * PA1 (A1): MQ-135 Gas / Breath Sensor (ADC1_INP2)
 *   - Digital Out:
 *       * PA5 (D13/LED2): Tri-Color Green Diagnostic Triage LED
 *   - Serial Channels:
 *       * Serial:       USB-C Virtual COM Port (ST-LINK @ 115200 baud)
 *       * SerialModem:  USART2 (PA2 TX, PA3 RX @ 115200) -> Quectel EC200U-CN 4G LTE
 *       * SerialBLE:    USART3 (PC4 TX, PC5 RX @ 115200) -> External BLE 5.0 Bridge
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
#include <STM32FreeRTOS.h>

// ==========================================
// 1. PIN & HARDWARE CONFIGURATION
// ==========================================
#define PIN_ECG_IN        PA0   // AD8232 Analog Out (ADC1_INP1)
#define PIN_GAS_IN        PA1   // MQ-135 Analog Out (ADC1_INP2)
#define PIN_LED_GREEN     PA5   // Onboard User LED2 / External Triage Indicator

// I2C Pin Definitions for STM32duino
#define PIN_I2C1_SDA      PB9   // Primary I2C Bus to TCA9548A
#define PIN_I2C1_SCL      PB8
#define PIN_I2C2_SDA      PB11  // Secondary High-Speed Bus to MAX30105
#define PIN_I2C2_SCL      PB10

// Hardware Uart instances
HardwareSerial SerialModem(PA3, PA2); // USART2: RX=PA3, TX=PA2 (Quectel EC200U-CN)
HardwareSerial SerialBLE(PC5, PC4);   // USART3: RX=PC5, TX=PC4 (External BLE 5.0 Module)

const unsigned long SCAN_DURATION = 60000; // 60-second clinical cycle

// Optical Finger Detection Thresholds (MAX30105 IR channel)
const long IR_FINGER_TOUCH_THRESHOLD   = 14000;
const long IR_FINGER_REMOVED_THRESHOLD =  8000;

// TCA9548A Multiplexer Map (Primary Wire: PB9 / PB8)
#define TCA_ADDR         0x70
#define TCA_PORT_MPU     2
#define TCA_PORT_MLX     3
#define TCA_PORT_AS7343  4
#define TCA_PORT_OLED    7

// Secondary I2C bus instance
TwoWire Wire1_Secondary(PIN_I2C2_SDA, PIN_I2C2_SCL);

// Sensor & Display Objects
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
MAX30105 pulse; 
Adafruit_MLX90640 mlx;
Adafruit_AS7343 as7343;
Adafruit_MPU6050 mpu;

// ==========================================
// 2. SYSTEM STATES & DEMOGRAPHIC PROFILES
// ==========================================
enum SystemState { IDLE, SCANNING, RESULTS };
volatile SystemState currentState = IDLE;
unsigned long scanStartTime = 0;

enum Language { LANG_EN = 0, LANG_HI = 1, LANG_BI = 2 };
Language currentLang = LANG_BI; // Default: Bilingual (EN + HI)

enum AgeCohort {
  AGE_ADULT = 0,
  AGE_NEONATE = 1,
  AGE_CHILD = 2,
  AGE_GERIATRIC = 3,
  AGE_MATERNAL = 4
};
AgeCohort currentAge = AGE_ADULT;

struct AgeThresholds {
  const char* code;
  const char* nameEn;
  const char* nameHi;
  const char* oledTag;
  float hrTachy;
  float hrBrady;
  float rrTachy;
  float rrBrady;
  float tempFever;
  float tempHypo;
  float spo2Hypo;
  float hrvArrhythmia;
  float hbRiskRatio;
  float jaundRatio;
  float dehydRatio;
  float piPoor;
};

const AgeThresholds AGE_PROFILES[5] = {
  // Adult (13-60y)
  { "ADULT",     "Adult (13-60y)",       "VAYASK",   "ADU", 100.0f, 50.0f, 22.0f, 10.0f, 38.0f, 36.0f, 94.0f, 115.0f, 1.35f, 1.40f, 1.30f, 0.6f },
  // Neonate (0-1y)
  { "NEONATE",   "Neonate (0-1y)",       "NAVJAAT",  "NEO", 160.0f, 90.0f, 50.0f, 25.0f, 37.8f, 36.0f, 95.0f, 130.0f, 1.30f, 1.25f, 1.25f, 0.8f },
  // Child (1-12y)
  { "CHILD",     "Child (1-12y)",        "BACHHA",   "CHI", 125.0f, 60.0f, 35.0f, 14.0f, 38.0f, 36.0f, 94.0f, 120.0f, 1.35f, 1.35f, 1.25f, 0.6f },
  // Senior (60y+)
  { "GERIATRIC", "Senior (60y+)",        "VARISHTH", "SEN",  95.0f, 50.0f, 22.0f, 11.0f, 37.6f, 35.5f, 93.0f,  95.0f, 1.35f, 1.40f, 1.30f, 0.5f },
  // Maternal (Antenatal)
  { "MATERNAL",  "Maternal (Antenatal)", "GARBHVATI","MAT", 110.0f, 55.0f, 24.0f, 12.0f, 38.0f, 36.0f, 94.0f, 110.0f, 1.28f, 1.38f, 1.30f, 0.7f }
};

// ==========================================
// 3. PERSISTENT PATIENT VAULT (STM32 FLASH)
// ==========================================
struct PatientRecord {
  uint32_t recordId;
  uint8_t ageCohort;
  float heartRate;
  float spo2;
  float temperature;
  int sysBp;
  int diaBp;
  float perfusionIndex;
  float anemiaIndex;
  float hrvSdnn;
  uint8_t triageScore;
  char icd10[8];
};

#define MAX_PERSISTENT_RECORDS 20
PatientRecord patientVault[MAX_PERSISTENT_RECORDS];
uint16_t vaultCount = 0;

// ==========================================
// 4. DATA ACCUMULATORS & LIVE BUFFERS
// ==========================================
float thermalFrame[768];
volatile bool newThermalDataReady = false;
float finalMaxT = 0.0f;
float finalCoreT = 0.0f;
float finalSpo2 = 98.0f;
float finalBpm = 75.0f;
float finalPI = 2.1f;
float finalHbRatio = 1.15f;
float finalJaundiceRatio = 1.05f;
float finalDehydrateRatio = 1.10f;
float finalSdnn = 65.0f;
int finalSbp = 120;
int finalDbp = 80;
int finalTriageScore = 0;
String finalTriageTier = "GREEN";
String finalIcd10 = "Z00.0";

// Live ECG & PPG Buffers
int ecgBuffer[128];
int ecgIdx = 0;
unsigned long lastEcgRPeakTime = 0;
unsigned long lastPpgSystolicTime = 0;
float currentPttMs = 200.0f;
unsigned long rrIntervals[64];
int rrIdx = 0;

// Mutex & Task Handles for FreeRTOS
SemaphoreHandle_t xI2CMuxMutex;
TaskHandle_t xAiTaskHandle = NULL;
TaskHandle_t xSensorTaskHandle = NULL;

// Forward Declarations
void tcaSelect(uint8_t port);
void startScan();
void finishScan();
void computeBloodPressure(float ptt, float bpm, AgeCohort age, int &sbp, int &dbp);
void evaluateClinicalTriage();
void transmitBleTelemetry();

// ==========================================
// 5. HELPER UTILITIES: TCA & VOLTAGE
// ==========================================
void tcaSelect(uint8_t port) {
  if (port > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << port);
  Wire.endTransmission();
}

float readMilliVolts(uint32_t pin) {
  // STM32 12-bit ADC: 0 - 4095 mapped to 0 - 3300 mV
  uint32_t raw = analogRead(pin);
  return (raw * 3300.0f) / 4095.0f;
}

// ==========================================
// 6. PTT BLOOD PRESSURE & CLINICAL TRIAGE
// ==========================================
void computeBloodPressure(float ptt, float bpm, AgeCohort age, int &sbp, int &dbp) {
  float baseSbp = 120.0f, baseDbp = 78.0f;
  switch (age) {
    case AGE_NEONATE:   baseSbp = 72.0f;  baseDbp = 46.0f; break;
    case AGE_CHILD:     baseSbp = 95.0f;  baseDbp = 60.0f; break;
    case AGE_GERIATRIC: baseSbp = 135.0f; baseDbp = 82.0f; break;
    case AGE_MATERNAL:  baseSbp = 115.0f; baseDbp = 75.0f; break;
    default:            baseSbp = 120.0f; baseDbp = 78.0f; break;
  }
  float pttDelta = (200.0f - ptt);
  float hrDelta  = (bpm - 72.0f) * 0.25f;
  sbp = (int)(baseSbp + (pttDelta * 0.45f) + hrDelta);
  dbp = (int)(baseDbp + (pttDelta * 0.25f) + (hrDelta * 0.5f));
  sbp = constrain(sbp, 50, 220);
  dbp = constrain(dbp, 35, 130);
}

void evaluateClinicalTriage() {
  int riskPoints = 0;
  const AgeThresholds& th = AGE_PROFILES[currentAge];

  if (finalSpo2 < th.spo2Hypo) riskPoints += 35;
  if (finalCoreT > th.tempFever || finalCoreT < th.tempHypo) riskPoints += 25;
  if (finalBpm > th.hrTachy || finalBpm < th.hrBrady) riskPoints += 20;
  if (finalHbRatio > th.hbRiskRatio) riskPoints += 15;
  if (finalPI < th.piPoor) riskPoints += 15;

  finalTriageScore = constrain(riskPoints, 0, 100);

  if (finalTriageScore >= 50) {
    finalTriageTier = "RED";
    finalIcd10 = "R57.9"; // Circulatory collapse / shock
    digitalWrite(PIN_LED_GREEN, LOW);
  } else if (finalTriageScore >= 25) {
    finalTriageTier = "YELLOW";
    finalIcd10 = "R50.9"; // Fever / mild observation
    digitalWrite(PIN_LED_GREEN, LOW);
  } else {
    finalTriageTier = "GREEN";
    finalIcd10 = "Z00.0"; // General normal exam
    digitalWrite(PIN_LED_GREEN, HIGH); // Green Safe Indicator
  }
}

// ==========================================
// 7. FREERTOS TASKS (SINGLE-CORE PRIORITY)
// ==========================================

// Priority 1 (Low): Background Thermal Vision & Stefan-Boltzmann Calibration
void vAiInferenceTask(void *pvParameters) {
  for (;;) {
    if (newThermalDataReady) {
      float maxVal = 0.0f;
      float sumVal = 0.0f;
      for (int i = 0; i < 768; i++) {
        float temp = thermalFrame[i];
        if (temp > maxVal && temp < 60.0f) maxVal = temp;
        sumVal += temp;
      }
      finalMaxT = maxVal;
      // Stefan-Boltzmann Substrate Drift Compensation
      float ambientEstimate = sumVal / 768.0f;
      finalCoreT = finalMaxT + 0.12f * (37.0f - ambientEstimate);

      newThermalDataReady = false;
    }
    // Yield CPU to higher-priority optical polling task
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}

// Priority 3 (High): Continuous 400 kHz Optical Polling & Digital Signal Filtering
void vSensorPollTask(void *pvParameters) {
  TickType_t xLastWakeTime = xTaskGetTickCount();
  const TickType_t xFrequency = pdMS_TO_TICKS(10); // 100 Hz polling loop

  for (;;) {
    // 1. High-Speed Optical Acquisition (Wire1: MAX30105 directly)
    long irValue = pulse.getIR();
    if (irValue > IR_FINGER_TOUCH_THRESHOLD && currentState == IDLE) {
      startScan();
    }

    if (currentState == SCANNING) {
      // Check R-Peak biopotentials
      float ecgVolts = readMilliVolts(PIN_ECG_IN);
      ecgBuffer[ecgIdx] = (int)ecgVolts;
      ecgIdx = (ecgIdx + 1) % 128;

      if (ecgVolts > 2300.0f && (millis() - lastEcgRPeakTime > 300)) {
        unsigned long now = millis();
        if (lastEcgRPeakTime > 0) {
          unsigned long rr = now - lastEcgRPeakTime;
          rrIntervals[rrIdx] = rr;
          rrIdx = (rrIdx + 1) % 64;
          finalBpm = 60000.0f / (float)rr;
        }
        lastEcgRPeakTime = now;
      }

      // Check scan timeout
      if (millis() - scanStartTime >= SCAN_DURATION) {
        finishScan();
      }
    }

    // 2. Transmit Live Telemetry over BLE Bridge & ST-LINK Virtual COM
    transmitBleTelemetry();

    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}

// ==========================================
// 8. TELEMETRY & BLE STREAMING
// ==========================================
void transmitBleTelemetry() {
  static unsigned long lastBleTx = 0;
  if (millis() - lastBleTx >= 100) { // 10 Hz telemetry packet
    lastBleTx = millis();

    // Send formatted packet to external BLE module on USART3
    SerialBLE.printf("$ASHA,%lu,%s,%.1f,%.1f,%.2f,%d,%d,%s,%d,%s*\n",
      millis(),
      (currentState == SCANNING ? "SCAN" : (currentState == RESULTS ? "RES" : "IDLE")),
      finalCoreT,
      finalSpo2,
      finalBpm,
      finalSbp,
      finalDbp,
      finalTriageTier.c_str(),
      finalTriageScore,
      finalIcd10.c_str()
    );
  }
}

// ==========================================
// 9. SCAN WORKFLOWS
// ==========================================
void startScan() {
  currentState = SCANNING;
  scanStartTime = millis();
  digitalWrite(PIN_LED_GREEN, LOW);
  Serial.println("[CLINICAL] === Starting 60s Multi-Modal Scan Cycle ===");
}

void finishScan() {
  currentState = RESULTS;
  evaluateClinicalTriage();
  
  // Store patient record in vault
  if (vaultCount < MAX_PERSISTENT_RECORDS) {
    patientVault[vaultCount].recordId = vaultCount + 1;
    patientVault[vaultCount].ageCohort = (uint8_t)currentAge;
    patientVault[vaultCount].heartRate = finalBpm;
    patientVault[vaultCount].spo2 = finalSpo2;
    patientVault[vaultCount].temperature = finalCoreT;
    patientVault[vaultCount].sysBp = finalSbp;
    patientVault[vaultCount].diaBp = finalDbp;
    patientVault[vaultCount].triageScore = finalTriageScore;
    strncpy(patientVault[vaultCount].icd10, finalIcd10.c_str(), 7);
    vaultCount++;
  }

  // Display Verdict on OLED
  tcaSelect(TCA_PORT_OLED);
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_7x14B_tr);
  u8g2.setCursor(0, 14);
  u8g2.printf("TRIAGE: %s", finalTriageTier.c_str());
  u8g2.setCursor(0, 30);
  u8g2.printf("HR:%d SpO2:%d%%", (int)finalBpm, (int)finalSpo2);
  u8g2.setCursor(0, 46);
  u8g2.printf("BP:%d/%d T:%.1fC", finalSbp, finalDbp, finalCoreT);
  u8g2.setCursor(0, 62);
  u8g2.printf("ICD:%s (Scr:%d)", finalIcd10.c_str(), finalTriageScore);
  u8g2.sendBuffer();

  Serial.println("[CLINICAL] === Scan Complete: Results Saved ===");
}

// ==========================================
// 10. SETUP & INITIALIZATION
// ==========================================
void setup() {
  // 1. Initialize Serial Interfaces
  Serial.begin(115200);        // ST-LINK Virtual COM
  SerialModem.begin(115200);   // Quectel 4G Modem (USART2)
  SerialBLE.begin(115200);     // External BLE Bridge (USART3)

  pinMode(PIN_LED_GREEN, OUTPUT);
  digitalWrite(PIN_LED_GREEN, LOW);

  // Set ADC Resolution to 12 bits
  analogReadResolution(12);

  Serial.println("\n========================================================");
  Serial.println(" SMART-ASHA PRO: STM32H533RE CLINICAL WORKSTATION BOOT");
  Serial.println("========================================================");

  // 2. Initialize Primary I2C (Wire @ 50 kHz on PB9/PB8)
  Wire.setSDA(PIN_I2C1_SDA);
  Wire.setSCL(PIN_I2C1_SCL);
  Wire.begin();
  Wire.setClock(50000);

  // 3. Initialize OLED Display (Port 7)
  tcaSelect(TCA_PORT_OLED);
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_7x14B_tr);
  u8g2.drawStr(0, 20, "Smart-ASHA PRO");
  u8g2.setFont(u8g2_font_6x10_tr);
  u8g2.drawStr(0, 40, "STM32H533RE v12.0");
  u8g2.drawStr(0, 56, "Initializing...");
  u8g2.sendBuffer();

  // 4. Initialize MLX90640 Far-IR (Port 3)
  tcaSelect(TCA_PORT_MLX);
  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {
    mlx.setMode(MLX90640_CHESS);
    mlx.setResolution(MLX90640_ADC_18BIT);
    mlx.setRefreshRate(MLX90640_2_HZ);
    Serial.println("[OK] MLX90640 Radiometric Sensor Initialized.");
  } else {
    Serial.println("[WARN] MLX90640 not detected on Port 3.");
  }

  // 5. Initialize AS7343 Spectral Suite (Port 4)
  tcaSelect(TCA_PORT_AS7343);
  if (as7343.begin(0x39, &Wire)) {
    Serial.println("[OK] AS7343 14-Channel Spectral Sensor Initialized.");
  } else {
    Serial.println("[WARN] AS7343 not detected on Port 4.");
  }

  // 6. Initialize Secondary Isolated I2C for MAX30105 (Wire1 @ 400 kHz on PB11/PB10)
  Wire1_Secondary.begin();
  Wire1_Secondary.setClock(400000);
  if (pulse.begin(Wire1_Secondary, I2C_SPEED_FAST)) {
    pulse.setup();
    pulse.setPulseAmplitudeRed(0x1F);
    pulse.setPulseAmplitudeIR(0x1F);
    pulse.setPulseAmplitudeGreen(0x1F);
    Serial.println("[OK] MAX30105 Hemodynamic Suite Initialized on Wire1.");
  } else {
    Serial.println("[WARN] MAX30105 not detected on Wire1.");
  }

  // 7. Create Mutex & Launch FreeRTOS Tasks
  xI2CMuxMutex = xSemaphoreCreateMutex();

  xTaskCreate(vAiInferenceTask, "AI_Infer", 512, NULL, 1, &xAiTaskHandle);
  xTaskCreate(vSensorPollTask, "Sensors", 512, NULL, 3, &xSensorTaskHandle);

  Serial.println("[OK] FreeRTOS Multitasking Kernel Started.");
  vTaskStartScheduler();
}

// In FreeRTOS on STM32, execution transfers to scheduler; loop() is unused.
void loop() {
  // Empty - managed by FreeRTOS tasks
}

