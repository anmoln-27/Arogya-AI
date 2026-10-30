import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/vitals_model.dart';
import '../models/referral_model.dart';

class ScreeningRecord {
  final String id;
  final String timestamp;
  final String patientName;
  final int age;
  final String gender;
  final String village;
  final double bpm;
  final double spo2;
  final double temp;
  final double pi;
  final int score;
  final String triage;
  final String urgency;
  final String destination;

  ScreeningRecord({
    required this.id,
    required this.timestamp,
    required this.patientName,
    required this.age,
    required this.gender,
    required this.village,
    required this.bpm,
    required this.spo2,
    required this.temp,
    required this.pi,
    required this.score,
    required this.triage,
    required this.urgency,
    required this.destination,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp,
    'patientName': patientName,
    'age': age,
    'gender': gender,
    'village': village,
    'bpm': bpm,
    'spo2': spo2,
    'temp': temp,
    'pi': pi,
    'score': score,
    'triage': triage,
    'urgency': urgency,
    'destination': destination,
  };

  factory ScreeningRecord.fromJson(Map<String, dynamic> j) => ScreeningRecord(
    id: j['id'] ?? '',
    timestamp: j['timestamp'] ?? '',
    patientName: j['patientName'] ?? 'Unknown',
    age: j['age'] ?? 30,
    gender: j['gender'] ?? 'Female',
    village: j['village'] ?? 'Local Village',
    bpm: (j['bpm'] as num?)?.toDouble() ?? 72.0,
    spo2: (j['spo2'] as num?)?.toDouble() ?? 98.0,
    temp: (j['temp'] as num?)?.toDouble() ?? 36.6,
    pi: (j['pi'] as num?)?.toDouble() ?? 1.2,
    score: (j['score'] as num?)?.toInt() ?? 0,
    triage: j['triage'] ?? 'NORMAL',
    urgency: j['urgency'] ?? 'Routine',
    destination: j['destination'] ?? 'Home Care',
  );
}

class StorageService {
  static const String _key = 'smart_asha_screenings_v1';

  static Future<List<ScreeningRecord>> getRecords() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? [];
    return raw.map((item) => ScreeningRecord.fromJson(jsonDecode(item))).toList();
  }

  static Future<void> saveRecord({
    required VitalsModel vitals,
    required ReferralModel referral,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final list = prefs.getStringList(_key) ?? [];

    final rec = ScreeningRecord(
      id: 'REC-${DateTime.now().millisecondsSinceEpoch}',
      timestamp: DateTime.now().toIso8601String().substring(0, 19).replaceAll('T', ' '),
      patientName: referral.patientName,
      age: referral.patientAge,
      gender: referral.patientGender,
      village: referral.village,
      bpm: vitals.bpm,
      spo2: vitals.spo2,
      temp: vitals.temp,
      pi: vitals.pi,
      score: vitals.score,
      triage: referral.triageLevel,
      urgency: referral.urgency,
      destination: referral.referralDestination,
    );

    list.insert(0, jsonEncode(rec.toJson()));
    await prefs.setStringList(_key, list);
  }

  static Future<String> generateCsv() async {
    final records = await getRecords();
    final buffer = StringBuffer();
    buffer.writeln('ID,Timestamp,Patient,Age,Gender,Village,HR_BPM,SpO2_Pct,Temp_C,PI_Pct,Score,Triage,Urgency,Destination');
    for (var r in records) {
      buffer.writeln('${r.id},"${r.timestamp}","${r.patientName}",${r.age},${r.gender},"${r.village}",${r.bpm},${r.spo2},${r.temp},${r.pi},${r.score},${r.triage},"${r.urgency}","${r.destination}"');
    }
    return buffer.toString();
  }

  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
