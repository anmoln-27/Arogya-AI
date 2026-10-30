import 'dart:convert';

/// Complete Vitals & Telemetry Model for Smart-ASHA
class VitalsModel {
  final String state; // 'IDLE', 'SCAN', 'RESULTS'
  final double bpm;
  final double spo2;
  final double pi;
  final double temp;
  final int score;
  final String triage;
  final String triageHi;
  final double sdnn;
  final double rmssd;
  final double pnn50;
  final double hb;
  final double jaund;
  final double dehy;
  final double asym;
  final int feverProb;
  final int rem;
  final int dur;
  final DateTime timestamp;

  VitalsModel({
    this.state = 'IDLE',
    this.bpm = 72.0,
    this.spo2 = 98.0,
    this.pi = 1.2,
    this.temp = 36.6,
    this.score = 0,
    this.triage = 'NORMAL',
    this.triageHi = 'सामान्य',
    this.sdnn = 45.0,
    this.rmssd = 38.0,
    this.pnn50 = 18.0,
    this.hb = 0.95,
    this.jaund = 0.88,
    this.dehy = 0.75,
    this.asym = 0.15,
    this.feverProb = 2,
    this.rem = 0,
    this.dur = 60,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory VitalsModel.fromJson(Map<String, dynamic> json) {
    return VitalsModel(
      state: json['state']?.toString().toUpperCase() ?? 
             json['status']?.toString().toUpperCase() ?? 'IDLE',
      bpm: (json['bpm'] as num?)?.toDouble() ?? 72.0,
      spo2: (json['spo2'] as num?)?.toDouble() ?? 98.0,
      pi: (json['pi'] as num?)?.toDouble() ?? 1.2,
      temp: (json['temp'] as num?)?.toDouble() ?? 36.6,
      score: (json['score'] as num?)?.toInt() ?? 0,
      triage: json['triage']?.toString() ?? 'NORMAL',
      triageHi: json['triage_hi']?.toString() ?? 'सामान्य',
      sdnn: (json['sdnn'] as num?)?.toDouble() ?? 45.0,
      rmssd: (json['rmssd'] as num?)?.toDouble() ?? 38.0,
      pnn50: (json['pnn50'] as num?)?.toDouble() ?? 18.0,
      hb: (json['hb'] as num?)?.toDouble() ?? 0.95,
      jaund: (json['jaund'] as num?)?.toDouble() ?? 0.88,
      dehy: (json['dehy'] as num?)?.toDouble() ?? 0.75,
      asym: (json['asym'] as num?)?.toDouble() ?? 0.15,
      feverProb: (json['fever_p'] as num?)?.toInt() ?? 2,
      rem: (json['rem'] as num?)?.toInt() ?? 0,
      dur: (json['dur'] as num?)?.toInt() ?? 60,
      timestamp: DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
    'state': state,
    'bpm': bpm,
    'spo2': spo2,
    'pi': pi,
    'temp': temp,
    'score': score,
    'triage': triage,
    'triage_hi': triageHi,
    'sdnn': sdnn,
    'rmssd': rmssd,
    'pnn50': pnn50,
    'hb': hb,
    'jaund': jaund,
    'dehy': dehy,
    'asym': asym,
    'fever_p': feverProb,
    'rem': rem,
    'dur': dur,
    'timestamp': timestamp.toIso8601String(),
  };

  /// Fail-Safe Simulator Profile A: Healthy Adult (GREEN)
  factory VitalsModel.profileA() => VitalsModel(
    state: 'RESULTS',
    bpm: 72.0,
    spo2: 98.5,
    pi: 2.1,
    temp: 36.6,
    score: 0,
    triage: 'NORMAL',
    triageHi: 'सामान्य',
    sdnn: 52.0,
    rmssd: 42.0,
    pnn50: 22.0,
    hb: 0.98,
    jaund: 0.82,
    dehy: 0.65,
    asym: 0.08,
    feverProb: 1,
    timestamp: DateTime.now(),
  );

  /// Fail-Safe Simulator Profile B: Febrile / Severe Anemia (RED)
  factory VitalsModel.profileB() => VitalsModel(
    state: 'RESULTS',
    bpm: 118.0,
    spo2: 91.0,
    pi: 0.35,
    temp: 39.4,
    score: 70,
    triage: 'CRITICAL',
    triageHi: 'गंभीर आपातकाल',
    sdnn: 18.0,
    rmssd: 14.0,
    pnn50: 3.0,
    hb: 0.42,
    jaund: 1.68,
    dehy: 1.55,
    asym: 0.45,
    feverProb: 94,
    timestamp: DateTime.now(),
  );

  /// Fail-Safe Simulator Profile C: Cardiac Stress / Tachycardia (YELLOW)
  factory VitalsModel.profileC() => VitalsModel(
    state: 'RESULTS',
    bpm: 105.0,
    spo2: 94.0,
    pi: 0.72,
    temp: 37.8,
    score: 40,
    triage: 'WARNING',
    triageHi: 'चेतावनी',
    sdnn: 28.0,
    rmssd: 22.0,
    pnn50: 8.0,
    hb: 0.72,
    jaund: 1.15,
    dehy: 1.12,
    asym: 0.22,
    feverProb: 48,
    timestamp: DateTime.now(),
  );
}
