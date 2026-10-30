import 'package:flutter_tts/flutter_tts.dart';
import '../models/vitals_model.dart';

enum AudioLanguage { hindi, english, mute }

class AudioGuidanceService {
  final FlutterTts _tts = FlutterTts();
  AudioLanguage _language = AudioLanguage.hindi;
  bool _isInitialized = false;

  AudioLanguage get language => _language;

  Future<void> init() async {
    if (_isInitialized) return;
    try {
      await _tts.setSpeechRate(0.5);
      await _tts.setVolume(1.0);
      await _tts.setPitch(1.0);
      _isInitialized = true;
    } catch (_) {}
  }

  void setLanguage(AudioLanguage lang) {
    _language = lang;
  }

  Future<void> speak(String textEn, String textHi) async {
    if (_language == AudioLanguage.mute) return;
    await init();

    try {
      if (_language == AudioLanguage.hindi) {
        await _tts.setLanguage('hi-IN');
        await _tts.speak(textHi);
      } else {
        await _tts.setLanguage('en-IN');
        await _tts.speak(textEn);
      }
    } catch (_) {}
  }

  Future<void> speakWelcome() async {
    await speak(
      'Smart-ASHA Clinical Workstation ready. Please position the patient forehead in front of the thermal sensor.',
      'स्मार्ट-आशा क्लिनिकल वर्कस्टेशन तैयार है। कृपया मरीज का माथा सेंसर के सामने रखें।',
    );
  }

  Future<void> speakScanStart(int duration) async {
    await speak(
      'Scan started. Hold steady for $duration seconds. Reading vitals and thermal imaging.',
      'जांच शुरू हो गई है। कृपया $duration सेकंड तक स्थिर बैठें।',
    );
  }

  Future<void> speakScanComplete(VitalsModel v) async {
    if (v.score >= 50) {
      await speak(
        'Critical alert! Severity score is ${v.score}. Oxygen level is ${v.spo2.round()} percent. Urgent referral to Primary Health Centre required.',
        'सावधान! खतरा स्कोर ${v.score} है। ऑक्सीजन ${v.spo2.round()} प्रतिशत है। मरीज को तुरंत प्राथमिक स्वास्थ्य केंद्र रेफर करें।',
      );
    } else if (v.score >= 25) {
      await speak(
        'Warning. Moderate risk detected with score ${v.score}. Schedule ANM checkup within 24 hours.',
        'ध्यान दें। मध्यम जोखिम दर्ज हुआ है। २४ घंटे के भीतर एएनएम या डॉक्टर से संपर्क करें।',
      );
    } else {
      await speak(
        'Screening complete. All vitals are within normal range. Oxygen is ${v.spo2.round()} percent.',
        'जांच पूरी हुई। सभी स्वास्थ्य मानक सामान्य हैं। ऑक्सीजन ${v.spo2.round()} प्रतिशत है।',
      );
    }
  }

  void stop() {
    _tts.stop();
  }
}
