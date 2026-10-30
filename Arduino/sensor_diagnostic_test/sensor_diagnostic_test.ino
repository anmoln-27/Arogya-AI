/*
 * ====================================================================================================
 *  SMART-ASHA HARDWARE HEALTH CHECK & SENSOR DIAGNOSTIC SUITE
 * ====================================================================================================
 *  Target Hardware: 7Semi ESP32-S3 EC200U 4G LTE Smart Modem
 *  Baud Rate: 115200
 *
 *  DIAGNOSTIC SCOPE:
 *   1. Primary I2C (Wire @ GPIO 8 SDA, GPIO 18 SCL):
 *      - TCA9548A Multiplexer (0x70)
 *      - Channel 2: MPU6050 6-Axis IMU (0x68) + Live Accelerometer read
 *      - Channel 3: MLX90640 Thermal Array (0x33)
 *      - Channel 4: AS7343 14-Channel Multi-Spectral (0x39)
 *      - Channel 7: SH1106 128x64 OLED (0x3C)
 *   2. Secondary I2C (Wire1 @ GPIO 16 SDA, GPIO 17 SCL):
 *      - MAX30105 Pulse/SpO2 (0x57) + Register ID check + Live Photodiode read
 *   3. Calibrated Analog Inputs (eFuse ADC):
 *      - GPIO 4: AD8232 ECG Front-End (ADC1_CH6)
 *      - GPIO 6: MQ-135 Gas / Respiratory Sensor (ADC1_CH5)
 * ====================================================================================================
 */

#include <Arduino.h>
#include <Wire.h>

// --- PIN DEFINITIONS ---
const int PIN_I2C_SDA_PRIMARY   = 8;
const int PIN_I2C_SCL_PRIMARY   = 18;
const int PIN_I2C_SDA_SECONDARY = 16;
const int PIN_I2C_SCL_SECONDARY = 17;

const int PIN_ECG_ANALOG        = 4;   // AD8232
const int PIN_GAS_ANALOG        = 6;   // MQ-135

#define TCA_ADDR 0x70

// TCA9548A Channel Switcher
bool tcaSelect(uint8_t channel) {
  if (channel > 7) return false;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << channel);
  return (Wire.endTransmission() == 0);
}

void tcaDisableAll() {
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(0x00);
  Wire.endTransmission();
}

// Quick I2C probe helper
bool probeAddress(TwoWire &bus, uint8_t addr) {
  bus.beginTransmission(addr);
  return (bus.endTransmission() == 0);
}

// Read single 8-bit register helper
int readRegister(TwoWire &bus, uint8_t devAddr, uint8_t regAddr) {
  bus.beginTransmission(devAddr);
  bus.write(regAddr);
  if (bus.endTransmission(false) != 0) return -1;
  if (bus.requestFrom((int)devAddr, 1) != 1) return -1;
  return bus.read();
}

void setup() {
  Serial.begin(115200);
  unsigned long startWait = millis();
  while (!Serial && (millis() - startWait < 3000)); // Wait for USB CDC on ESP32-S3

  Serial.println("\n");
  Serial.println("======================================================================");
  Serial.println("       SMART-ASHA: COMPLETE HARDWARE SENSOR DIAGNOSTIC SUITE         ");
  Serial.println("======================================================================");

  // Initialize Primary I2C (50 kHz for long wiring / multiplexer stability)
  Serial.print("[INIT] Primary I2C (GPIO 8 SDA, GPIO 18 SCL @ 50kHz)... ");
  Wire.begin(PIN_I2C_SDA_PRIMARY, PIN_I2C_SCL_PRIMARY, 50000);
  Serial.println("DONE.");

  // Initialize Secondary I2C (400 kHz for MAX30105 FIFO speed)
  Serial.print("[INIT] Secondary I2C (GPIO 16 SDA, GPIO 17 SCL @ 400kHz)... ");
  Wire1.begin(PIN_I2C_SDA_SECONDARY, PIN_I2C_SCL_SECONDARY, 400000);
  Serial.println("DONE.");

  // Set ADC Attenuation for 0 - 3.3V range
  analogSetAttenuation(ADC_11db);
  Serial.println("[INIT] ADC Attenuation calibrated to 11dB (0 - 3.1V range).");

  Serial.println("\n--- RUNNING INITIAL STATIC HARDWARE CHECK ---");

  // 1. Check TCA9548A
  bool tcaPresent = probeAddress(Wire, TCA_ADDR);
  if (tcaPresent) {
    Serial.println("  [PASS] TCA9548A I2C Multiplexer detected at 0x70");
  } else {
    Serial.println("  [FAIL] TCA9548A Multiplexer NOT FOUND at 0x70! Check 3.3V power and SDA(8)/SCL(18).");
  }

  // 2. Scan Multiplexer Ports
  if (tcaPresent) {
    for (uint8_t ch = 0; ch < 8; ch++) {
      tcaSelect(ch);
      Serial.printf("  -> Scanning MUX Channel %d: ", ch);
      uint8_t count = 0;
      for (uint8_t addr = 1; addr < 127; addr++) {
        if (addr == TCA_ADDR) continue;
        if (probeAddress(Wire, addr)) {
          Serial.printf("Found 0x%02X ", addr);
          count++;
        }
      }
      if (count == 0) Serial.print("[Empty / No Device]");
      
      // Expected mappings confirmation
      if (ch == 2) Serial.print(" <-- [Expected: MPU6050 @ 0x68]");
      if (ch == 3) Serial.print(" <-- [Expected: MLX90640 @ 0x33]");
      if (ch == 4) Serial.print(" <-- [Expected: AS7343 @ 0x39]");
      if (ch == 7) Serial.print(" <-- [Expected: SH1106 OLED @ 0x3C]");
      Serial.println();
    }
  }

  // 3. Check MAX30105 on Wire1
  Serial.print("  -> Scanning Wire1 (Secondary Bus): ");
  bool maxPresent = probeAddress(Wire1, 0x57);
  if (maxPresent) {
    int partId = readRegister(Wire1, 0x57, 0xFF);
    Serial.printf("[PASS] MAX30105 found at 0x57 (Part ID: 0x%02X, Expected: 0x15)\n", partId);

    // Wake up MAX30105 and turn on Red LED for verification
    Wire1.beginTransmission(0x57);
    Wire1.write(0x09); // Mode Configuration
    Wire1.write(0x03); // SpO2 mode (Red + IR)
    Wire1.endTransmission();

    Wire1.beginTransmission(0x57);
    Wire1.write(0x0C); // LED1 (Red) Pulse Amplitude
    Wire1.write(0x1F); // ~6.4mA
    Wire1.endTransmission();
  } else {
    Serial.println("[FAIL] MAX30105 NOT FOUND on GPIO 16/17! Check 3.3V power and wiring.");
  }

  // Wake up MPU6050 if detected
  tcaSelect(2);
  if (probeAddress(Wire, 0x68)) {
    Wire.beginTransmission(0x68);
    Wire.write(0x6B); // PWR_MGMT_1
    Wire.write(0x00); // Wake up
    Wire.endTransmission();
    Serial.println("  [INFO] MPU6050 Sleep Mode cleared (Sensor Active).");
  }

  Serial.println("----------------------------------------------------------------------");
  Serial.println("STARTING CONTINUOUS LIVE SENSOR MONITOR (Updates every 1.5s)");
  Serial.println("Tap, touch, or move sensors to verify real-time data response!");
  Serial.println("----------------------------------------------------------------------\n");
  delay(2000);
}

void loop() {
  Serial.println("======================= [ LIVE DIAGNOSTIC STREAM ] =======================");

  // -------------------------------------------------------------
  // 1. MAX30105 (Pulse / SpO2 - Wire1)
  // -------------------------------------------------------------
  Serial.print("❤️ [MAX30105 @ Wire1]: ");
  if (probeAddress(Wire1, 0x57)) {
    // Read FIFO raw bytes if available
    Wire1.beginTransmission(0x57);
    Wire1.write(0x07); // FIFO Data Register
    Wire1.endTransmission(false);
    if (Wire1.requestFrom(0x57, 6) == 6) {
      uint32_t red = ((uint32_t)Wire1.read() << 16) | ((uint32_t)Wire1.read() << 8) | Wire1.read();
      uint32_t ir  = ((uint32_t)Wire1.read() << 16) | ((uint32_t)Wire1.read() << 8) | Wire1.read();
      red &= 0x03FFFF;
      ir  &= 0x03FFFF;
      Serial.printf("OK | Red: %6u | IR: %6u | Finger Contact: %s\n", 
                    red, ir, (ir > 10000 ? "DETECTED (ON SENSOR)" : "NO FINGER"));
    } else {
      Serial.println("OK (Bus Active, awaiting FIFO ready)");
    }
  } else {
    Serial.println("OFFLINE / DISCONNECTED ❌");
  }

  // -------------------------------------------------------------
  // 2. MPU6050 (Motion / IMU - Port 2)
  // -------------------------------------------------------------
  Serial.print("📐 [MPU6050  @ Port 2]: ");
  tcaSelect(2);
  if (probeAddress(Wire, 0x68)) {
    Wire.beginTransmission(0x68);
    Wire.write(0x3B); // ACCEL_XOUT_H
    Wire.endTransmission(false);
    if (Wire.requestFrom(0x68, 6) == 6) {
      int16_t ax = (Wire.read() << 8) | Wire.read();
      int16_t ay = (Wire.read() << 8) | Wire.read();
      int16_t az = (Wire.read() << 8) | Wire.read();
      // Roughly convert to G (~16384 LSB/g at +/-2g)
      float gX = ax / 16384.0;
      float gY = ay / 16384.0;
      float gZ = az / 16384.0;
      Serial.printf("OK | Accel: X=%+5.2fg  Y=%+5.2fg  Z=%+5.2fg\n", gX, gY, gZ);
    } else {
      Serial.println("OK (I2C Responded)");
    }
  } else {
    // Check fallback Port 1
    tcaSelect(1);
    if (probeAddress(Wire, 0x68)) {
      Serial.println("OK (NOTE: Detected on MUX Port 1 instead of Port 2!)");
    } else {
      Serial.println("OFFLINE / DISCONNECTED ❌");
    }
  }

  // -------------------------------------------------------------
  // 3. MLX90640 (Thermal Camera - Port 3)
  // -------------------------------------------------------------
  Serial.print("🌡️ [MLX90640 @ Port 3]: ");
  tcaSelect(3);
  if (probeAddress(Wire, 0x33)) {
    // Read status register 0x8000
    Wire.beginTransmission(0x33);
    Wire.write(0x80);
    Wire.write(0x00);
    Wire.endTransmission(false);
    if (Wire.requestFrom(0x33, 2) == 2) {
      uint16_t status = (Wire.read() << 8) | Wire.read();
      Serial.printf("OK | Sensor Active (Status Reg: 0x%04X)\n", status);
    } else {
      Serial.println("OK (ACK received on 0x33)");
    }
  } else {
    Serial.println("OFFLINE / DISCONNECTED ❌");
  }

  // -------------------------------------------------------------
  // 4. AS7343 (Multi-Spectral - Port 4)
  // -------------------------------------------------------------
  Serial.print("🌈 [AS7343   @ Port 4]: ");
  tcaSelect(4);
  if (probeAddress(Wire, 0x39)) {
    // Read CHIP ID register (0x00 or 0x92 depending on page)
    int chipId = readRegister(Wire, 0x39, 0x92);
    Serial.printf("OK | 14-Channel Sensor Online (Reg ID: 0x%02X)\n", chipId);
  } else {
    Serial.println("OFFLINE / DISCONNECTED ❌");
  }

  // -------------------------------------------------------------
  // 5. SH1106 OLED (Display - Port 7)
  // -------------------------------------------------------------
  Serial.print("🖥️ [OLED     @ Port 7]: ");
  tcaSelect(7);
  if (probeAddress(Wire, 0x3C)) {
    Serial.println("OK | 128x64 I2C Display Responded at 0x3C");
  } else {
    Serial.println("OFFLINE / DISCONNECTED ❌ (Check Port 7 wiring or 0x3D)");
  }

  // -------------------------------------------------------------
  // 6. AD8232 ECG (Analog GPIO 4)
  // -------------------------------------------------------------
  uint32_t ecgMv = analogReadMilliVolts(PIN_ECG_ANALOG);
  uint16_t ecgRaw = analogRead(PIN_ECG_ANALOG);
  Serial.print("⚡ [AD8232   @ GPIO 4]: ");
  Serial.printf("Live: %4u mV (Raw: %4u) | Status: ", ecgMv, ecgRaw);
  if (ecgMv < 100 || ecgMv > 3100) {
    Serial.println("LEADS-OFF / DISCONNECTED (Floating rail)");
  } else {
    Serial.println("LEADS CONNECTED / ACTIVE SIGNAL");
  }

  // -------------------------------------------------------------
  // 7. MQ-135 Gas / Respiratory (Analog GPIO 6)
  // -------------------------------------------------------------
  uint32_t gasMv = analogReadMilliVolts(PIN_GAS_ANALOG);
  uint16_t gasRaw = analogRead(PIN_GAS_ANALOG);
  Serial.print("💨 [MQ-135   @ GPIO 6]: ");
  Serial.printf("Live: %4u mV (Raw: %4u) | Status: ", gasMv, gasRaw);
  if (gasMv < 50) {
    Serial.println("NO POWER / CHECK 5V HEATER PIN");
  } else if (gasMv > 2500) {
    Serial.println("VERY HIGH GAS / PRE-HEAT SATURATION");
  } else {
    Serial.println("NORMAL AMBIENT BASELINE");
  }

  Serial.println("--------------------------------------------------------------------------\n");
  delay(1500);
}
