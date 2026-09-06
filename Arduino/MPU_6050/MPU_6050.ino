#include <Wire.h>
#include <SPI.h>
#include "MAX30105.h"        
#include <Adafruit_MLX90640.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// --- PIN DEFINITIONS ---
const int CS_PIN = 14; 
const int ecgPin = 4;   
const int gasPin = 7;

// --- DUAL I2C ENGINES ---
TwoWire I2CHub = TwoWire(0);   // Bus 0: Pins 8 (SDA) & 18 (SCL)
TwoWire I2CPulse = TwoWire(1); // Bus 1: Pins 41 (SDA) & 42 (SCL)

// --- OBJECTS ---
MAX30105 pulse;
Adafruit_MLX90640 mlx;
Adafruit_MPU6050 mpu;
float thermalFrame[768];

bool pulseOnline = false;
bool mpuOnline = false;

// Custom TCA Select for the I2CHub object
void tcaSelect(uint8_t i) {
  I2CHub.beginTransmission(0x70);
  I2CHub.write(1 << i);
  I2CHub.endTransmission();
}

void setup() {
  Serial.begin(115200);
  delay(3000); 

  Serial.println("--- SMART-ASHA: PRODUCTION MODE ---");

  // 1. INITIALIZE HUB BUS (MPU & Thermal)
  I2CHub.begin(8, 18, 100000);
  
  tcaSelect(1); // Open the door to the MPU-6050
  if (mpu.begin(0x68, &I2CHub)) {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpuOnline = true;
    Serial.println("[OK] MPU-6050 Online");
  }

  tcaSelect(3); // Open the door to the Thermal Camera
  if (mlx.begin(MLX90640_I2CADDR_DEFAULT, &I2CHub)) {
    mlx.setRefreshRate(MLX90640_4_HZ);
    Serial.println("[OK] Thermal Online");
  }

  // 2. INITIALIZE PULSE BUS (Private Lane)
  I2CPulse.begin(41, 42, 100000);
  if (pulse.begin(I2CPulse, I2C_SPEED_FAST)) {
    pulse.setup(); 
    pulseOnline = true;
    Serial.println("[OK] Pulse Online");
  }

  // 3. INITIALIZE GSR/ECG (SPI Bus)
  pinMode(CS_PIN, OUTPUT); digitalWrite(CS_PIN, HIGH);
  SPI.begin(21, 39, 40, CS_PIN); 
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x06); delay(50); // RESET
  SPI.transfer(0x11); delay(50); // Wakeup
  SPI.transfer(0x08); delay(50); // Start
  SPI.transfer(0x10);            // Read Continuous (RDATAC)
  digitalWrite(CS_PIN, HIGH);
  Serial.println("[OK] SPI GSR/ECG Active");

  Serial.println("Timestamp,ECG,GSR,Gas,Pulse_IR,Temp_Max,Accel_X");
}

void loop() {
  // A. Analog/SPI Signals
  int rawECG = analogRead(ecgPin);
  int rawGas = analogRead(gasPin);
  digitalWrite(CS_PIN, LOW);
  long gsr = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
  digitalWrite(CS_PIN, HIGH);

  // B. Pulse Signal (Bus 1)
  long irValue = (pulseOnline) ? pulse.getIR() : 0;

  // C. Motion Signal (Bus 0 - Port 1)
  float accX = 0;
  if (mpuOnline) {
    tcaSelect(1);
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    accX = a.acceleration.x;
  }

  // D. Thermal Signal (Bus 0 - Port 3 - Sampled every 500ms)
  float maxT = 35.0; 
  if (millis() % 500 < 30) {
    tcaSelect(3);
    if (mlx.getFrame(thermalFrame) == 0) {
      maxT = -99;
      for (int i=0; i<768; i++) if(thermalFrame[i] > maxT) maxT = thermalFrame[i];
    }
  }

  // --- CSV OUTPUT FOR LOGGER ---
  Serial.print(millis()); Serial.print(",");
  Serial.print(rawECG);   Serial.print(",");
  Serial.print(gsr);      Serial.print(",");
  Serial.print(rawGas);   Serial.print(",");
  Serial.print(irValue);  Serial.print(",");
  Serial.print(maxT);     Serial.print(",");
  Serial.println(accX);

  delay(15); // Consistent sampling rate
}