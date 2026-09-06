#include <Wire.h>
#include <SPI.h>
#include "MAX30105.h"        
#include <Adafruit_MLX90640.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

const int CS_PIN = 14; 
const int ecgPin = 4;   const int gasPin = 7;

TwoWire I2CHub = TwoWire(0);   
TwoWire I2CPulse = TwoWire(1); 

MAX30105 pulse; Adafruit_MLX90640 mlx; Adafruit_MPU6050 mpu;
float thermalFrame[768];
bool pulseOnline = false; bool mpuOnline = false;

void tcaSelect(uint8_t i) {
  I2CHub.beginTransmission(0x70);
  I2CHub.write(1 << i);
  I2CHub.endTransmission();
  delay(2); // Small delay to let the Hub settle
}

void setup() {
  Serial.begin(115200);
  delay(3000); 

  Serial.println("--- SMART-ASHA: FINAL HARDWARE SYNC ---");

  // 1. Bus 0: Hub Setup
  I2CHub.begin(8, 18, 100000);
  
  // Try to find MPU on Port 1
  tcaSelect(1);
  if (mpu.begin(0x68, &I2CHub)) {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpuOnline = true;
    Serial.println("[OK] MPU-6050: Detected");
  } else {
    Serial.println("[!!] MPU-6050: NOT FOUND on SD1/SC1");
  }

  // Thermal on Port 3
  tcaSelect(3);
  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &I2CHub)) {
    mlx.setRefreshRate(MLX90640_4_HZ);
    Serial.println("[OK] Thermal: Detected");
  }

  // 2. Bus 1: Direct Pulse Setup
  I2CPulse.begin(41, 42, 100000);
  if (pulse.begin(I2CPulse, I2C_SPEED_FAST)) {
    pulse.setup();
    pulseOnline = true;
    Serial.println("[OK] Pulse: Detected");
  }

  // 3. SPI GSR Setup
  pinMode(CS_PIN, OUTPUT); digitalWrite(CS_PIN, HIGH);
  SPI.begin(21, 39, 40, CS_PIN); 
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x06); delay(50); 
  SPI.transfer(0x11); delay(50); 
  SPI.transfer(0x08); delay(50); 
  SPI.transfer(0x10); 
  digitalWrite(CS_PIN, HIGH);

  Serial.println("Timestamp,ECG,GSR,Gas,Pulse_IR,Temp_Max,Accel_X");
}

void loop() {
  // Analog/SPI Reads (Fast)
  int ecg = analogRead(ecgPin);
  int gas = analogRead(gasPin);
  digitalWrite(CS_PIN, LOW);
  long gsr = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
  digitalWrite(CS_PIN, HIGH);

  // Pulse (Bus 1 - Always fast)
  long irValue = (pulseOnline) ? pulse.getIR() : 0;

  // Accel (Bus 0 - Port 1)
  float accX = 0;
  if (mpuOnline) {
    tcaSelect(1); 
    sensors_event_t a, g, temp;
    if(mpu.getEvent(&a, &g, &temp)) {
      accX = a.acceleration.x;
    }
  }

  // Thermal (Bus 0 - Port 3 - Slower)
  float maxT = 35.0;
  if (millis() % 1000 < 50) { // Read thermal only once per second to save Bus time
    tcaSelect(3);
    if (mlx.getFrame(thermalFrame) == 0) {
      maxT = -99;
      for (int i=0; i<768; i++) if(thermalFrame[i] > maxT) maxT = thermalFrame[i];
    }
  }

  // CSV Output
  Serial.print(millis()); Serial.print(",");
  Serial.print(ecg);      Serial.print(",");
  Serial.print(gsr);      Serial.print(",");
  Serial.print(gas);      Serial.print(",");
  Serial.print(irValue);  Serial.print(",");
  Serial.print(maxT);     Serial.print(",");
  Serial.println(accX);

  delay(20); 
}