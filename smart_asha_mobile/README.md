# 🩺 Smart-ASHA — 100% Offline Flutter Mobile App

An end-to-end, zero-internet Clinical Workstation application built with **Flutter**, designed specifically for **ASHA (Accredited Social Health Activist)** community health workers in remote rural and tribal villages.

---

## ⚡ Key Highlights for Hackathon Demonstrations

1. **100% Offline Autonomy:**
   * Runs in **Airplane Mode** with zero cellular network or Wi-Fi router.
   * Connects peer-to-peer to the ESP32-S3 via **Bluetooth Low Energy (BLE 5.0)** within ~10 meters.
2. **Real-Time Dual-Channel Oscilloscope:**
   * Hardware-accelerated 60 FPS Canvas rendering for **CH1 PPG Pulse (Green)** and **CH2 ECG Lead I (Cyan)** with sweep cursor.
3. **24×32 Thermal Face Heatmap (MLX90640):**
   * Real-time thermal array rendering with high-contrast **Ironbow colormap**, forehead fever hotspot detection, and facial temperature asymmetry ($\Delta T$).
4. **Deterministic Offline Triage Engine:**
   * Generates **ICD-10 diagnostic codes**, emergency/urgent triage tiers, and clinical summaries without calling any cloud API.
5. **Ayushman Bharat Referral Slip & Vector QR Code:**
   * 100% offline QR generation via `qr_flutter` (contains complete patient vitals, score, and ICD-10 data).
   * **1-Tap WhatsApp Tele-Consultation:** Dispatches a structured clinical summary directly to the Primary Health Centre (PHC) medical officer.
6. **Voice of ASHA (आवाज):**
   * Offline bilingual text-to-speech audio feedback in **Hindi (`hi-IN`)** and **English (`en-IN`)**.
7. **Built-in Fail-Safe Simulator (Essential for Demos):**
   * Tap the **tuning fork icon (tune)** on the app bar to cycle through:
     * **Profile A:** Healthy Adult (GREEN, Score 0)
     * **Profile B:** Febrile / Severe Anemia (RED Emergency, Score 70, Temp 39.4°C, SpO₂ 91%)
     * **Profile C:** Cardiac Stress / Tachycardia (YELLOW Warning, Score 40)
   * Guaranteed flawless demonstration even if the ESP32 hardware battery runs out during judging!

---

## 📂 Project Architecture

```
smart_asha_mobile/
├── pubspec.yaml                          # Dependencies (BLE, TTS, QR, Sharing)
├── android/
│   └── app/src/main/AndroidManifest.xml  # Android 12+ BLE & Location permissions
└── lib/
    ├── main.dart                         # Dark Clinical Theme & App Entrypoint
    ├── models/
    │   ├── vitals_model.dart             # Telemetry parser & 3 Simulator Profiles
    │   └── referral_model.dart           # ICD-10 model, QR serializer, WhatsApp formatter
    ├── services/
    │   ├── ble_service.dart              # flutter_blue_plus GATT client & Auto-reconnect
    │   ├── audio_guidance_service.dart   # Offline Hindi/English TTS Audio Engine
    │   ├── offline_triage_engine.dart    # 100% Offline Rule-Based ICD-10 Diagnostic Engine
    │   └── storage_service.dart          # Local SharedPreferences offline screening log
    ├── widgets/
    │   ├── oscilloscope_widget.dart      # 60 FPS PPG + ECG dual-channel CustomPainter
    │   ├── thermal_heatmap_widget.dart   # 24x32 MLX90640 face heatmap CustomPainter
    │   ├── triage_gauge_widget.dart      # Conic arc severity score meter
    │   └── vital_card_widget.dart        # Star Performer clinical metric cards
    └── screens/
        ├── dashboard_screen.dart         # Main Clinical Command Center
        ├── referral_screen.dart          # Ayushman Bharat Referral Slip with Offline QR
        └── history_screen.dart           # Offline screening history with CSV export
```

---

## 🚀 How to Run & Build

### 1. Prerequisites
* Install Flutter SDK: [https://flutter.dev/docs/get-started/install](https://flutter.dev/docs/get-started/install)
* Connect an Android device (via USB with USB Debugging enabled) or open an Android emulator.

### 2. Install Dependencies
```bash
cd smart_asha_mobile
flutter pub get
```

### 3. Run Live on Connected Device
```bash
flutter run
```

### 4. Build Production Offline Release APK
```bash
flutter build apk --release
```
The compiled APK will be generated at:
`build/app/outputs/flutter-apk/app-release.apk`
You can transfer this `.apk` via USB drive, Bluetooth, or WhatsApp to any ASHA worker's Android phone/tablet for instant installation.

---

## 📡 Bluetooth GATT Specification (ESP32-S3)

* **Service UUID:** `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
* **Characteristic UUID:** `beb5483e-36e1-4688-b7f5-ea07361b26a8` (Notify, Read, Write)
* **Command Set:**
  * `SCAN`: Triggers multi-sensor acquisition.
  * `FAST`: Toggles Express 10s Demo Mode.
  * `NORMAL`: Reverts to Standard 60s Clinical Diagnostic Mode.
