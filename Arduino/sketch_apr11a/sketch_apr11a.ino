/*
 * Smart-ASHA v2.0: OLED Diagnostic Script
 * Hardware: ESP32-S3 + TCA9548A Hub + SSD1306 OLED
 * OLED Connection: TCA Port 0 (SD0/SC0)
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1 // Sharing reset pin or not used
#define SCREEN_ADDRESS 0x3C // Standard for 0.96" OLEDs

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// TCA9548A Port Selector
void tcaSelect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(0x70); // TCA Hub Address
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  
  // Initialize I2C on Pins 8 (SDA) and 18 (SCL)
  Wire.begin(8, 18);
  Wire.setClock(400000); // Fast mode for smoother thermal heatmap rendering

  Serial.println("Initializing OLED on Port 0...");

  // CRITICAL: Must select Port 0 before calling display.begin
  tcaSelect(0);

  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed. Check wiring on SD0/SC0."));
    for(;;); // Don't proceed if display fails
  }

  // Clear the buffer and show a Splash Screen
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(15, 20);
  display.println("SMART-ASHA v2.0");
  display.setCursor(25, 35);
  display.println("Triage Active");
  display.display(); 
  
  delay(2000);
}

void loop() {
  // Step 1: Open Port 0 to update the screen
  tcaSelect(0);

  display.clearDisplay();
  display.setCursor(0,0);
  display.setTextSize(1);
  display.println("SYSTEM STATUS: OK");
  display.drawLine(0, 12, 128, 12, WHITE);

  // Example placeholder for your sensor data
  display.setCursor(0, 20);
  display.print("Thermal: "); display.println("READY");
  display.print("Spectral: "); display.println("SYNCED");
  display.print("Acoustic: "); display.println("WAITING");

  display.display(); // Push everything to the screen

  delay(1000); 
}