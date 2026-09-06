#include <Wire.h>
#include "MAX30105.h"        // Port 0
#include <MPU6050_light.h>   // Port 1
#include <Adafruit_SH110X.h> // Port 4

#define TCA_ADDR 0x70
#define I2C_SDA 8
#define I2C_SCL 14 

MAX30105 particleSensor;
MPU6050 mpu(Wire);
Adafruit_SH1106G display(128, 64, &Wire, -1);

void tcaSelect(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);

  // Initialize OLED for visual confirmation
  tcaSelect(4);
  display.begin(0x3C, true);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0,0);
  display.println("Smart-ASHA v1.0");
  display.println("Master Scan Mode");
  display.display();

  // Verify I2C Sensors
  tcaSelect(0);
  if (particleSensor.begin()) Serial.println("MAX30102: PASS");
  
  tcaSelect(1);
  if (mpu.begin() == 0) Serial.println("MPU-6050: PASS");
}

void loop() {
  // Read All Active Analog Sensors [cite: 257-261]
  int ecg = analogRead(1);
  int gsr = analogRead(4);
  int voc = analogRead(5);
  
  // Read I2C Sensors [cite: 263-264]
  tcaSelect(1); mpu.update();
  float resp = mpu.getAccZ();

  // Output to Serial Monitor
  Serial.printf("ECG:%d | GSR:%d | VOC:%d | Resp:%.3f\n", ecg, gsr, voc, resp);
  
  delay(500); 
}
