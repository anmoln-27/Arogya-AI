#include <Wire.h>
#include <SPI.h>
#include "MAX30105.h"        
#include <Adafruit_MLX90640.h>

const int SCK_PIN = 21; const int MISO_PIN = 39; const int MOSI_PIN = 40; const int CS_PIN = 14;
const int ecgPin = 4;   const int gasPin = 7;

MAX30105 pulseSensor;
Adafruit_MLX90640 mlx;
float thermalFrame[768];

float filteredECG = 0;
const float alpha = 0.02; 
int currentLabel = 0;     
int loopCounter = 0;
float maxT = 0;

void tcaSelect(uint8_t i) {
  Wire.beginTransmission(0x70);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 18);
  Wire.setClock(400000); 

  pinMode(CS_PIN, OUTPUT); digitalWrite(CS_PIN, HIGH);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, CS_PIN);
  
  delay(100);
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x06); delay(10); 
  SPI.transfer(0x11); delay(10); 
  SPI.transfer(0x08);            
  digitalWrite(CS_PIN, HIGH);

  tcaSelect(5); pulseSensor.begin(Wire, I2C_SPEED_FAST); pulseSensor.setup();
  tcaSelect(3); mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire); mlx.setRefreshRate(MLX90640_4_HZ);

  Serial.println("Timestamp,ECG,GSR,Gas,Pulse_IR,Temp_Max,Label");
}

void loop() {
  if (Serial.available() > 0) {
    char inChar = Serial.read();
    if (inChar == '0') currentLabel = 0;
    if (inChar == '1') currentLabel = 1;
    if (inChar == '2') currentLabel = 2;
  }

  int rawECG = analogRead(ecgPin);
  filteredECG = (alpha * rawECG) + ((1.0 - alpha) * filteredECG);
  int gasVal = analogRead(gasPin);

  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x00); SPI.transfer(0x00); SPI.transfer(0x00); 
  long gsrVal = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
  digitalWrite(CS_PIN, HIGH);

  tcaSelect(5); long irPulse = pulseSensor.getIR();

  if (loopCounter % 50 == 0) {
    tcaSelect(3);
    if (mlx.getFrame(thermalFrame) == 0) {
      maxT = -99;
      for (int i=0; i<768; i++) if(thermalFrame[i] > maxT) maxT = thermalFrame[i];
    }
  }

  Serial.print(millis());    Serial.print(",");
  Serial.print(filteredECG); Serial.print(",");
  Serial.print(gsrVal);      Serial.print(",");
  Serial.print(gasVal);      Serial.print(",");
  Serial.print(irPulse);     Serial.print(",");
  Serial.print(maxT);        Serial.print(",");
  Serial.println(currentLabel);

  loopCounter++;
  delay(11); 
}
