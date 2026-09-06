#include <Wire.h>
#include <SPI.h>
#include "MAX30105.h"        
#include <Adafruit_MLX90640.h>

// --- PINS ---
const int CS_PIN = 14; 
const int ecgPin = 4;   const int gasPin = 7;

// --- OBJECTS ---
MAX30105 pulse; 
Adafruit_MLX90640 mlx;
float thermalFrame[768];
bool pulseOnline = false;

// TCA Hub Selection (Bus 0)
void tcaSelect(uint8_t i) {
  Wire.beginTransmission(0x70);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  delay(3000); 

  Serial.println("--- SMART-ASHA: SYSTEM FINAL SYNC ---");

  // 1. HUB BUS (MPU & Thermal) - Pins 8 & 18
  Wire.begin(8, 18);
  Wire.setClock(100000); 

  // WAKE UP MPU-6050 (PORT 1) MANUALLY
  tcaSelect(1);
  delay(50);
  Wire.beginTransmission(0x68);
  Wire.write(0x6B); Wire.write(0x00); // Wake up command
  if (Wire.endTransmission() == 0) {
    Serial.println("[OK] MPU-6050: Woken and Ready");
  }

  // START THERMAL (PORT 3)
  tcaSelect(3);
  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {
    mlx.setRefreshRate(MLX90640_4_HZ);
    Serial.println("[OK] Thermal: Detected");
  }

  // 2. PULSE BUS (Private Lane) - Pins 41 & 42
  Wire1.begin(41, 42);
  if (pulse.begin(Wire1, I2C_SPEED_FAST)) {
    pulse.setup(); 
    pulseOnline = true;
    Serial.println("[OK] Pulse: Detected");
  }

  // 3. SPI GSR/ECG SETUP
  pinMode(CS_PIN, OUTPUT); digitalWrite(CS_PIN, HIGH);
  SPI.begin(21, 39, 40, CS_PIN); 
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x06); delay(50); SPI.transfer(0x11); delay(50); 
  SPI.transfer(0x08); delay(50); SPI.transfer(0x10); 
  digitalWrite(CS_PIN, HIGH);
  Serial.println("[OK] SPI Bio-Sensors Active");

  Serial.println("Timestamp,ECG,GSR,Gas,Pulse_IR,Temp_Max,Accel_X,Accel_Y");
}

void loop() {
  // A. ANALOG & SPI (Fast)
  int ecg = analogRead(ecgPin);
  int gas = analogRead(gasPin);
  digitalWrite(CS_PIN, LOW);
  long gsr = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
  digitalWrite(CS_PIN, HIGH);

  // B. PULSE (Wire1)
  long irValue = (pulseOnline) ? pulse.getIR() : 0;

  // C. MPU RAW DATA (Hub Port 1)
  float accX = 0, accY = 0;
  tcaSelect(1);
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  if (Wire.requestFrom(0x68, 4, true) == 4) {
    int16_t rawX = Wire.read() << 8 | Wire.read();
    int16_t rawY = Wire.read() << 8 | Wire.read();
    accX = rawX / 16384.0 * 9.81;
    accY = rawY / 16384.0 * 9.81;
  }

  // D. THERMAL (Hub Port 3 - Every 1 second to keep loop fast)
  float maxT = 35.0;
  if (millis() % 1000 < 20) {
    tcaSelect(3);
    if (mlx.getFrame(thermalFrame) == 0) {
      maxT = -99;
      for (int i=0; i<768; i++) if(thermalFrame[i] > maxT) maxT = thermalFrame[i];
    }
  }

  // --- FINAL CSV OUTPUT ---
  Serial.print(millis()); Serial.print(",");
  Serial.print(ecg);      Serial.print(",");
  Serial.print(gsr);      Serial.print(",");
  Serial.print(gas);      Serial.print(",");
  Serial.print(irValue);  Serial.print(",");
  Serial.print(maxT);     Serial.print(",");
  Serial.print(accX);     Serial.print(",");
  Serial.println(accY);

  delay(20); 
}