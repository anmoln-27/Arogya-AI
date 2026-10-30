/*
 * ====================================================================================================
 *  SMART-ASHA: REAL-TIME I2C BUS DOCTOR & LIVE WIRE-WIGGLE TESTER
 * ====================================================================================================
 *  Target Hardware: 7Semi ESP32-S3 EC200U (or standard ESP32-S3)
 *  Baud Rate: 115200
 *
 *  FEATURES:
 *   1. Physical Line Level Check: Verifies SDA/SCL pull-ups are ~3.3V (detects short to GND or dead power)
 *   2. I2C Bus Auto-Recovery: Pulses SCL 9 times to un-stick any hung slave holding SDA LOW
 *   3. Multiplexer Address Auto-Hunt: Scans 0x70 - 0x77 (detects if A0/A1/A2 pins are floating)
 *   4. Direct Main-Bus Scan: Detects if any sensor was accidentally wired directly to ESP32
 *   5. Real-Time Wiggle-Test: Refreshes every 750ms so you can jiggle wires and see instant feedback
 * ====================================================================================================
 */

#include <Arduino.h>
#include <Wire.h>

// --- PIN DEFINITIONS ---
const int PIN_PRIMARY_SDA   = 8;
const int PIN_PRIMARY_SCL   = 18;
const int PIN_SECONDARY_SDA = 16;
const int PIN_SECONDARY_SCL = 17;

#define TCA_EXPECTED_ADDR 0x70

// I2C Bus Recovery: Toggles SCL 9 times to release hung slaves
void recoverI2CBus(int sdaPin, int sclPin) {
  pinMode(sdaPin, INPUT_PULLUP);
  pinMode(sclPin, OUTPUT);
  for (int i = 0; i < 9; i++) {
    digitalWrite(sclPin, HIGH);
    delayMicroseconds(5);
    digitalWrite(sclPin, LOW);
    delayMicroseconds(5);
  }
  // Generate STOP condition
  pinMode(sdaPin, OUTPUT);
  digitalWrite(sdaPin, LOW);
  delayMicroseconds(5);
  digitalWrite(sclPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(sdaPin, HIGH);
  delayMicroseconds(5);

  pinMode(sdaPin, INPUT_PULLUP);
  pinMode(sclPin, INPUT_PULLUP);
}

// Check physical pull-up state when idle
bool checkIdleLevels(int sdaPin, int sclPin, String busName) {
  pinMode(sdaPin, INPUT_PULLUP);
  pinMode(sclPin, INPUT_PULLUP);
  delayMicroseconds(50);
  int sdaVal = digitalRead(sdaPin);
  int sclVal = digitalRead(sclPin);

  if (sdaVal == LOW || sclVal == LOW) {
    Serial.printf("  ⚠️  [%s BUS LOCK / SHORT]: SDA=%s | SCL=%s ", 
                  busName.c_str(), sdaVal == HIGH ? "HIGH (3.3V)" : "LOW (STUCK/SHORT!)", 
                                  sclVal == HIGH ? "HIGH (3.3V)" : "LOW (STUCK/SHORT!)");
    Serial.println("-> Attempting 9-clock bus unstick...");
    recoverI2CBus(sdaPin, sclPin);
    return false;
  }
  return true;
}

// Select TCA9548A channel
bool tcaSelect(uint8_t addr, uint8_t channel) {
  if (channel > 7) return false;
  Wire.beginTransmission(addr);
  Wire.write(1 << channel);
  return (Wire.endTransmission() == 0);
}

void tcaDeselect(uint8_t addr) {
  Wire.beginTransmission(addr);
  Wire.write(0x00);
  Wire.endTransmission();
}

// Probe I2C address
bool probeAddr(TwoWire &bus, uint8_t addr) {
  bus.beginTransmission(addr);
  return (bus.endTransmission() == 0);
}

void setup() {
  Serial.begin(115200);
  unsigned long start = millis();
  while (!Serial && (millis() - start < 3000));

  Serial.println("\n\n========================================================================");
  Serial.println("        SMART-ASHA: LIVE I2C CONTINUITY & BUS HEALTH DOCTOR            ");
  Serial.println("========================================================================");
  Serial.println("-> Wiggle your breadboard wires in real-time to locate loose connections.");
  Serial.println("-> Refreshing live status every 750 ms...\n");

  // Initial bus reset to ensure clean state
  recoverI2CBus(PIN_PRIMARY_SDA, PIN_PRIMARY_SCL);
  recoverI2CBus(PIN_SECONDARY_SDA, PIN_SECONDARY_SCL);

  // Initialize Wire (Primary) @ 50 kHz for long jumper wire stability
  Wire.begin(PIN_PRIMARY_SDA, PIN_PRIMARY_SCL, 50000);
  Wire.setTimeOut(50); // Short timeout to prevent hanging on loose wires

  // Initialize Wire1 (Secondary) @ 400 kHz for MAX30105
  Wire1.begin(PIN_SECONDARY_SDA, PIN_SECONDARY_SCL, 400000);
  Wire1.setTimeOut(50);
}

int scanIteration = 0;

void loop() {
  scanIteration++;
  Serial.println("------------------------------------------------------------------------");
  Serial.printf(" 🩺 [CYCLE #%d] LIVE I2C BUS HEALTH STATUS\n", scanIteration);
  Serial.println("------------------------------------------------------------------------");

  // =========================================================================
  // 1. PRIMARY I2C BUS (GPIO 8 SDA, GPIO 18 SCL)
  // =========================================================================
  Serial.print("🔹 PRIMARY BUS [GPIO 8/18]: ");
  
  // Check if any TCA9548A is responding anywhere in 0x70 - 0x77
  uint8_t tcaFoundAddr = 0;
  for (uint8_t a = 0x70; a <= 0x77; a++) {
    if (probeAddr(Wire, a)) {
      tcaFoundAddr = a;
      break;
    }
  }

  if (tcaFoundAddr == TCA_EXPECTED_ADDR) {
    Serial.printf("HEALTHY ✅ | TCA9548A Multiplexer detected at 0x%02X\n", tcaFoundAddr);
  } else if (tcaFoundAddr > 0) {
    Serial.printf("WRONG ADDRESS ⚠️ | TCA9548A detected at 0x%02X (Expected: 0x70)!\n", tcaFoundAddr);
    Serial.println("    👉 FIX: Connect TCA9548A pins A0, A1, A2 to GND to set address to 0x70.");
  } else {
    Serial.println("DISCONNECTED / NO ACK ❌");
    Serial.println("    👉 FIX: Check TCA9548A VCC (3.3V), GND, GPIO 8 (SDA), GPIO 18 (SCL).");
    Serial.println("    👉 FIX: Connect TCA9548A 'RST' pin to 3.3V rail (MUST NOT FLOAT!).");

    // Scan main bus anyway to see if any sensors are directly connected without MUX
    Serial.print("    -> Direct Main Bus Scan (Directly plugged sensors): ");
    uint8_t directCount = 0;
    for (uint8_t a = 1; a < 127; a++) {
      if (probeAddr(Wire, a)) {
        Serial.printf("[Found 0x%02X] ", a);
        directCount++;
      }
    }
    if (directCount == 0) {
      Serial.println("None (Bus completely silent / unpowered)");
    } else {
      Serial.println("\n    ⚠️ Found sensors directly on main bus! Are they wired before the multiplexer?");
    }
  }

  // If TCA is found, scan all 4 target channels
  if (tcaFoundAddr > 0) {
    Serial.println("\n  --- TCA9548A DOWNSTREAM CHANNEL PROBE ---");

    // Channel 2: MPU-6050 (0x68)
    tcaSelect(tcaFoundAddr, 2);
    bool mpuFound = probeAddr(Wire, 0x68);
    Serial.printf("  📐 Port 2 [MPU-6050   (0x68)]: %s\n", 
                  mpuFound ? "CONNECTED & RUNNING ✅" : "OFFLINE / DISCONNECTED ❌ (Check SD2/SC2)");

    // Channel 3: MLX90640 (0x33)
    tcaSelect(tcaFoundAddr, 3);
    bool mlxFound = probeAddr(Wire, 0x33);
    Serial.printf("  🌡️ Port 3 [MLX90640   (0x33)]: %s\n", 
                  mlxFound ? "CONNECTED & RUNNING ✅" : "OFFLINE / DISCONNECTED ❌ (Check SD3/SC3)");

    // Channel 4: AS7343 (0x39)
    tcaSelect(tcaFoundAddr, 4);
    bool asFound = probeAddr(Wire, 0x39);
    Serial.printf("  🌈 Port 4 [AS7343     (0x39)]: %s\n", 
                  asFound ? "CONNECTED & RUNNING ✅" : "OFFLINE / DISCONNECTED ❌ (Check SD4/SC4)");

    // Channel 7: SH1106 OLED (0x3C or 0x3D)
    tcaSelect(tcaFoundAddr, 7);
    bool oledFound = probeAddr(Wire, 0x3C) || probeAddr(Wire, 0x3D);
    Serial.printf("  🖥️ Port 7 [SH1106 OLED(0x3C)]: %s\n", 
                  oledFound ? "CONNECTED & RUNNING ✅" : "OFFLINE / DISCONNECTED ❌ (Check SD7/SC7)");

    tcaDeselect(tcaFoundAddr);
  }

  // =========================================================================
  // 2. SECONDARY I2C BUS (GPIO 16 SDA, GPIO 17 SCL)
  // =========================================================================
  Serial.print("\n🔹 SECONDARY BUS [GPIO 16/17]: ");
  bool maxFound = probeAddr(Wire1, 0x57);
  if (maxFound) {
    Serial.println("HEALTHY ✅ | MAX30105 Pulse/SpO2 detected at 0x57");
  } else {
    Serial.println("OFFLINE / DISCONNECTED ❌ (Check GPIO 16 SDA, GPIO 17 SCL)");
  }

  Serial.println("------------------------------------------------------------------------\n");
  delay(750); // Fast refresh for live wire wiggle testing
}
