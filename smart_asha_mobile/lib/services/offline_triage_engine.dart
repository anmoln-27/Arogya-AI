import '../models/vitals_model.dart';
import '../models/referral_model.dart';

/// 100% Offline Clinical Decision Support Engine
/// Deterministic ICD-10 rule-based diagnostic algorithm
class OfflineTriageEngine {
  static ReferralModel evaluate({
    required VitalsModel vitals,
    String patientName = 'Unknown Patient',
    int patientAge = 35,
    String patientGender = 'Female',
    String village = 'Gram Panchayat Kherli',
    String ashaId = 'ASHA-RAJ-1042',
  }) {
    final findings = <String>[];
    final icd = <IcdCode>[];
    final diff = <String>[];
    final recs = <String>[];

    // 1. Oxygenation
    if (vitals.spo2 < 90) {
      findings.add('Severe arterial hypoxia detected (SpO₂ ${vitals.spo2.round()}%)');
      icd.add(IcdCode(code: 'R09.02', desc: 'Hypoxemia'));
      diff.add('Acute Respiratory Distress / Severe Pneumonia');
    } else if (vitals.spo2 < 94) {
      findings.add('Moderate hypoxemia (SpO₂ ${vitals.spo2.round()}%)');
      icd.add(IcdCode(code: 'R09.02', desc: 'Hypoxemia'));
      diff.add('Lower respiratory tract infection');
    }

    // 2. Pulse / Cardiac
    if (vitals.bpm > 100) {
      findings.add('Sinus tachycardia (Pulse ${vitals.bpm.round()} BPM)');
      icd.add(IcdCode(code: 'R00.0', desc: 'Tachycardia, unspecified'));
      diff.add('Febrile tachycardia / Systemic stress');
    } else if (vitals.bpm < 50) {
      findings.add('Sinus bradycardia (Pulse ${vitals.bpm.round()} BPM)');
      icd.add(IcdCode(code: 'R00.1', desc: 'Bradycardia, unspecified'));
    }

    // 3. Temperature & Fever
    if (vitals.temp >= 38.5) {
      findings.add('High grade fever (Core temp ${vitals.temp.toStringAsFixed(1)}°C)');
      icd.add(IcdCode(code: 'R50.9', desc: 'Fever, unspecified'));
      diff.add('Acute febrile illness (Malaria / Dengue / Typhoid)');
    } else if (vitals.temp >= 37.5) {
      findings.add('Low grade fever (Temp ${vitals.temp.toStringAsFixed(1)}°C)');
      icd.add(IcdCode(code: 'R50.81', desc: 'Fever presenting with conditions classified elsewhere'));
    }

    // 4. Multi-spectral Anemia Screen (AS7343)
    if (vitals.hb < 0.65) {
      findings.add('Severe pallor & optical hemoglobin deficiency (Hb index ${vitals.hb.toStringAsFixed(2)})');
      icd.add(IcdCode(code: 'D64.9', desc: 'Anemia, unspecified'));
      diff.add('Nutritional iron deficiency anemia');
    } else if (vitals.hb < 0.85) {
      findings.add('Mild-to-moderate pallor screen (Hb index ${vitals.hb.toStringAsFixed(2)})');
      icd.add(IcdCode(code: 'D64.9', desc: 'Anemia, unspecified'));
    }

    // 5. Autonomic HRV Stress
    if (vitals.sdnn < 20) {
      findings.add('Severely suppressed Heart Rate Variability (SDNN ${vitals.sdnn.toStringAsFixed(1)} ms) — acute physiological stress');
      icd.add(IcdCode(code: 'R94.31', desc: 'Abnormal electrocardiogram'));
      diff.add('Severe autonomic exhaustion / Septic shock risk');
    }

    // 6. Dehydration & Jaundice
    if (vitals.dehy > 1.3) {
      findings.add('NIR multi-spectral hydration deficit — positive dehydration screening');
      icd.add(IcdCode(code: 'E86.0', desc: 'Dehydration'));
      diff.add('Acute gastrointestinal loss / Heat stress');
    }

    if (vitals.jaund > 1.4) {
      findings.add('Optical bilirubin absorption elevation — scleral jaundice suspicion');
      icd.add(IcdCode(code: 'R17', desc: 'Unspecified jaundice'));
      diff.add('Hepatic / Hemolytic hyperbilirubinemia');
    }

    if (findings.isEmpty) {
      findings.add('All multi-system physiological parameters within expected normal baseline');
      icd.add(IcdCode(code: 'Z00.00', desc: 'General adult medical examination'));
    }

    // Determine Triage Level & Actions
    final score = vitals.score;
    String triageLevel;
    String urgency;
    String referralDestination;

    if (score >= 50 || vitals.spo2 < 90 || vitals.temp >= 39.0) {
      triageLevel = 'RED';
      urgency = 'Immediate Emergency';
      referralDestination = 'Primary Health Centre (PHC) / 108 Ambulance';
      recs.add('Immediate ambulance dispatch to nearest 24/7 PHC or District Hospital');
      recs.add('Administer supplemental oxygen if available; keep patient in recovery posture');
      recs.add('Continuous monitoring of SpO₂ and heart rate during transport');
      if (vitals.temp >= 38.5) recs.add('Cold sponging on forehead/limbs to reduce hyperthermia');
    } else if (score >= 25 || vitals.spo2 < 94 || vitals.temp >= 37.8 || vitals.hb < 0.65) {
      triageLevel = 'YELLOW';
      urgency = 'Urgent (Within 24 Hours)';
      referralDestination = 'Health & Wellness Sub-Centre / Auxiliary Nurse Midwife (ANM)';
      recs.add('Schedule ANM / Medical Officer review within 24 hours');
      recs.add('Ensure oral rehydration solution (ORS) and hydration intake');
      recs.add('Repeat screening in 6 hours to monitor vital trajectory');
      if (vitals.hb < 0.85) recs.add('Iron & Folic Acid (IFA) therapeutic compliance verification');
    } else {
      triageLevel = 'GREEN';
      urgency = 'Routine Care';
      referralDestination = 'Home Care / Routine ASHA Surveillance';
      recs.add('Patient stable; continue normal daily activities');
      recs.add('Maintain balanced hydration, nutrition, and maternal/child health guidelines');
      recs.add('Next routine community screening as per monthly village roster');
    }

    return ReferralModel(
      patientName: patientName,
      patientAge: patientAge,
      patientGender: patientGender,
      village: village,
      ashaId: ashaId,
      triageLevel: triageLevel,
      urgency: urgency,
      clinicalSummary: findings.join('. ') + '.',
      icd10Codes: icd,
      differentialDiagnosis: diff,
      recommendations: recs,
      referralDestination: referralDestination,
      vitals: vitals,
    );
  }
}
