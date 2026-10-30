import 'dart:convert';
import 'vitals_model.dart';

class IcdCode {
  final String code;
  final String desc;
  IcdCode({required this.code, required this.desc});

  Map<String, dynamic> toJson() => {'code': code, 'desc': desc};
}

class ReferralModel {
  final String patientName;
  final int patientAge;
  final String patientGender;
  final String village;
  final String ashaId;
  final String triageLevel; // 'RED', 'YELLOW', 'GREEN'
  final String urgency;
  final String clinicalSummary;
  final List<IcdCode> icd10Codes;
  final List<String> differentialDiagnosis;
  final List<String> recommendations;
  final String referralDestination;
  final VitalsModel vitals;
  final DateTime createdAt;

  ReferralModel({
    required this.patientName,
    required this.patientAge,
    required this.patientGender,
    required this.village,
    required this.ashaId,
    required this.triageLevel,
    required this.urgency,
    required this.clinicalSummary,
    required this.icd10Codes,
    required this.differentialDiagnosis,
    required this.recommendations,
    required this.referralDestination,
    required this.vitals,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  /// Compresses critical clinical data into a lightweight JSON string for offline QR codes
  String toQrString() {
    return jsonEncode({
      'p': patientName,
      'a': patientAge,
      'g': patientGender,
      'v': village,
      'triage': triageLevel,
      'score': vitals.score,
      'spo2': vitals.spo2.round(),
      'bpm': vitals.bpm.round(),
      'temp': double.parse(vitals.temp.toStringAsFixed(1)),
      'urg': urgency,
      'dest': referralDestination,
      'time': createdAt.toIso8601String().substring(0, 16),
      'icd': icd10Codes.map((c) => c.code).toList(),
    });
  }

  /// WhatsApp formatted clinical dispatch message for remote doctor consultation
  String toWhatsAppMessage() {
    final buffer = StringBuffer();
    buffer.writeln('🚨 *SMART-ASHA CLINICAL REFERRAL DISPATCH* 🚨');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('👤 *Patient:* $patientName ($patientAge y/o $patientGender)');
    buffer.writeln('📍 *Location:* $village | *ASHA ID:* $ashaId');
    buffer.writeln('🚨 *Triage Level:* $triageLevel ($urgency)');
    buffer.writeln('📊 *Severity Score:* ${vitals.score}/100');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('💓 *Vitals:*');
    buffer.writeln('• SpO₂: ${vitals.spo2.round()}%');
    buffer.writeln('• Pulse: ${vitals.bpm.round()} BPM');
    buffer.writeln('• Temp: ${vitals.temp.toStringAsFixed(1)}°C');
    buffer.writeln('• Perfusion Index: ${vitals.pi.toStringAsFixed(2)}%');
    buffer.writeln('• SDNN HRV: ${vitals.sdnn.toStringAsFixed(1)} ms');
    buffer.writeln('• Hb Ratio: ${vitals.hb.toStringAsFixed(2)}');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('📋 *Clinical Summary:*');
    buffer.writeln(clinicalSummary);
    buffer.writeln('');
    buffer.writeln('🏷️ *ICD-10:* ' + icd10Codes.map((c) => '${c.code} (${c.desc})').join(', '));
    buffer.writeln('🏥 *Referral Destination:* $referralDestination');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('Generated via Smart-ASHA Edge Workstation');
    return buffer.toString();
  }
}
