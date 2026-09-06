// 1. MUST BE AT THE VERY TOP (Using BG96 as a Quectel fallback)
#define TINY_GSM_MODEM_BG96 

// 2. INCLUDE LIBRARY IMMEDIATELY AFTER DEFINE
#include <TinyGsmClient.h>

#define SerialMon Serial
#define SerialAT Serial1
7
// UART pins for your 7Semi ESP32-S3
#define MODEM_TX 17 
#define MODEM_RX 18

TinyGsm modem(SerialAT);

void setup() {
  SerialMon.begin(115200);
  delay(10);
  
  SerialAT.begin(115200, SERIAL_8N1, MODEM_RX, MODEM_TX);
  delay(3000);
  
  SerialMon.println("Initializing modem (Using Quectel Fallback)...");
  modem.restart();
  
  SerialMon.println("Enabling GPS/GNSS...");
  modem.enableGPS();
  
  SerialMon.println("GPS Enabled. Waiting for a valid fix...");
}

void loop() {
  float lat = 0.0, lon = 0.0;
  
  if (modem.getGPS(&lat, &lon)) {
    SerialMon.println("--- GPS FIX ACQUIRED ---");
    SerialMon.print("Latitude:  ");
    SerialMon.println(lat, 6);
    SerialMon.print("Longitude: ");
    SerialMon.println(lon, 6);
  } else {
    SerialMon.println("Searching for satellites... (Keep antenna near a window!)");
  }
  
  delay(2000); 
}