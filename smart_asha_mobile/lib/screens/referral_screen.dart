import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import '../models/referral_model.dart';
import '../services/storage_service.dart';

class ReferralScreen extends StatefulWidget {
  final ReferralModel referral;

  const ReferralScreen({Key? key, required this.referral}) : super(key: key);

  @override
  State<ReferralScreen> createState() => _ReferralScreenState();
}

class _ReferralScreenState extends State<ReferralScreen> {
  late TextEditingController _nameCtrl;
  late TextEditingController _ageCtrl;
  late TextEditingController _villageCtrl;
  bool _saved = false;

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(text: widget.referral.patientName);
    _ageCtrl = TextEditingController(text: widget.referral.patientAge.toString());
    _villageCtrl = TextEditingController(text: widget.referral.village);
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _ageCtrl.dispose();
    _villageCtrl.dispose();
    super.dispose();
  }

  Color get triageColor {
    if (widget.referral.triageLevel == 'RED') return const Color(0xFFEF4444);
    if (widget.referral.triageLevel == 'YELLOW') return const Color(0xFFF59E0B);
    return const Color(0xFF10B981);
  }

  Future<void> _shareWhatsApp() async {
    final msg = widget.referral.toWhatsAppMessage();
    final url = Uri.parse('whatsapp://send?text=${Uri.encodeComponent(msg)}');
    try {
      if (await canLaunchUrl(url)) {
        await launchUrl(url);
      } else {
        await Share.share(msg, subject: 'Smart-ASHA Referral Slip');
      }
    } catch (_) {
      await Share.share(msg, subject: 'Smart-ASHA Referral Slip');
    }
  }

  Future<void> _saveRecord() async {
    await StorageService.saveRecord(
      vitals: widget.referral.vitals,
      referral: widget.referral,
    );
    setState(() => _saved = true);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('✅ Screening record saved locally to device storage!'),
        backgroundColor: Color(0xFF10B981),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final ref = widget.referral;
    final v = ref.vitals;

    return Scaffold(
      backgroundColor: const Color(0xFF0B0F19),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Ayushman Bharat Referral', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: Icon(_saved ? Icons.bookmark_added : Icons.bookmark_border, color: const Color(0xFF00E5FF)),
            tooltip: 'Save to Offline Log',
            onPressed: _saved ? null : _saveRecord,
          ),
          IconButton(
            icon: const Icon(Icons.share, color: Colors.white),
            tooltip: 'Share via WhatsApp / Telemedicine',
            onPressed: _shareWhatsApp,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Referral Card Container
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white.withOpacity(0.08)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text('🏥 AYUSHMAN BHARAT', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF00E5FF))),
                          Text('स्मार्ट आशा रेफरल पर्ची • Smart-ASHA Referral Slip', style: TextStyle(fontSize: 10, color: Colors.white54)),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: triageColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: triageColor),
                        ),
                        child: Text(
                          '${ref.triageLevel} (${ref.urgency})',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: triageColor),
                        ),
                      ),
                    ],
                  ),
                  const Divider(color: Colors.white12, height: 28),

                  // Offline QR Code + Patient Summary Row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Vector QR Code (100% Offline via qr_flutter)
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: QrImageView(
                          data: ref.toQrString(),
                          version: QrVersions.auto,
                          size: 110,
                          backgroundColor: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 14),

                      // Patient & Vitals Summary
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              ref.patientName,
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                            ),
                            Text(
                              '${ref.patientAge} Y / ${ref.patientGender} • ${ref.village}',
                              style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.6)),
                            ),
                            const SizedBox(height: 8),
                            _bulletVital('SpO₂', '${v.spo2.round()}%', v.spo2 < 94 ? const Color(0xFFEF4444) : Colors.white),
                            _bulletVital('Heart Rate', '${v.bpm.round()} BPM', v.bpm > 100 ? const Color(0xFFF59E0B) : Colors.white),
                            _bulletVital('Core Temp', '${v.temp.toStringAsFixed(1)}°C', v.temp >= 38 ? const Color(0xFFEF4444) : Colors.white),
                            _bulletVital('Severity Score', '${v.score}/100', triageColor),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const Divider(color: Colors.white12, height: 28),

                  // Clinical Findings
                  const Text('📋 CLINICAL SUMMARY', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white70, letterSpacing: 0.5)),
                  const SizedBox(height: 6),
                  Text(ref.clinicalSummary, style: const TextStyle(fontSize: 13, height: 1.4, color: Colors.white)),
                  const SizedBox(height: 16),

                  // ICD-10 Codes
                  const Text('🏷️ ICD-10 DIAGNOSTIC CODES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white70, letterSpacing: 0.5)),
                  const SizedBox(height: 6),
                  ...ref.icd10Codes.map((c) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('• ${c.code}: ', style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF00E5FF), fontSize: 12)),
                        Expanded(child: Text(c.desc, style: const TextStyle(fontSize: 12, color: Colors.white70))),
                      ],
                    ),
                  )),
                  const SizedBox(height: 16),

                  // Recommendations
                  const Text('💊 CLINICAL RECOMMENDATIONS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white70, letterSpacing: 0.5)),
                  const SizedBox(height: 6),
                  ...ref.recommendations.map((r) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('• ', style: TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold)),
                        Expanded(child: Text(r, style: const TextStyle(fontSize: 12, color: Colors.white70))),
                      ],
                    ),
                  )),
                  const SizedBox(height: 16),

                  // Referral Destination
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: triageColor.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: triageColor.withOpacity(0.4)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.local_hospital, color: triageColor, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('REFERRAL DESTINATION', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: triageColor)),
                              Text(ref.referralDestination, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // WhatsApp Tele-consultation Share Button
            ElevatedButton.icon(
              onPressed: _shareWhatsApp,
              icon: const Icon(Icons.send, color: Colors.white),
              label: const Text(
                'DISPATCH TO DOCTOR VIA WHATSAPP',
                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF25D366), // WhatsApp Green
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _bulletVital(String label, String val, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 2),
      child: Row(
        children: [
          Text('$label: ', style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.5))),
          Text(val, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color, fontFamily: 'monospace')),
        ],
      ),
    );
  }
}
