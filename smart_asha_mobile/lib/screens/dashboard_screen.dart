import 'package:flutter/material.dart';
import '../models/vitals_model.dart';
import '../services/ble_service.dart';
import '../services/audio_guidance_service.dart';
import '../services/offline_triage_engine.dart';
import '../widgets/oscilloscope_widget.dart';
import '../widgets/thermal_heatmap_widget.dart';
import '../widgets/triage_gauge_widget.dart';
import '../widgets/vital_card_widget.dart';
import 'referral_screen.dart';
import 'history_screen.dart';

class DashboardScreen extends StatefulWidget {
  final BleService bleService;
  final AudioGuidanceService audioService;

  const DashboardScreen({
    Key? key,
    required this.bleService,
    required this.audioService,
  }) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  VitalsModel _vitals = VitalsModel();
  ConnectionStatus _connStatus = ConnectionStatus.disconnected;
  bool _isExpressMode = false;

  @override
  void initState() {
    super.initState();
    widget.bleService.vitalsStream.listen((v) {
      if (mounted) {
        setState(() => _vitals = v);
        if (v.state == 'RESULTS') {
          widget.audioService.speakScanComplete(v);
        }
      }
    });

    widget.bleService.statusStream.listen((s) {
      if (mounted) {
        setState(() => _connStatus = s);
      }
    });

    // Initial audio welcome
    Future.delayed(const Duration(milliseconds: 600), () {
      widget.audioService.speakWelcome();
    });
  }

  void _toggleExpressMode() {
    setState(() => _isExpressMode = !_isExpressMode);
    widget.bleService.sendCommand(_isExpressMode ? 'FAST' : 'NORMAL');
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(_isExpressMode ? '⚡ Express 10s Scan Mode Activated' : '⏱️ Standard 60s Clinical Diagnostic Scan Activated'),
        duration: const Duration(seconds: 2),
        backgroundColor: const Color(0xFF1E293B),
      ),
    );
  }

  void _triggerScan() {
    widget.bleService.sendCommand('SCAN');
    widget.audioService.speakScanStart(_isExpressMode ? 10 : 60);
  }

  void _openReferral() {
    final referral = OfflineTriageEngine.evaluate(vitals: _vitals);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ReferralScreen(referral: referral),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0F19),
      appBar: _buildAppBar(),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildConnectionBanner(),
            const SizedBox(height: 12),

            // Live 60fps Oscilloscope
            OscilloscopeWidget(
              bpm: _vitals.bpm,
              isScanning: _vitals.state == 'SCAN',
            ),
            const SizedBox(height: 12),

            // Triage Severity Gauge
            TriageGaugeWidget(
              score: _vitals.score,
              triage: _vitals.triage,
              triageHi: _vitals.triageHi,
            ),
            const SizedBox(height: 12),

            // 4 Star Performers Grid
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 10,
              crossAxisSpacing: 10,
              childAspectRatio: 1.45,
              children: [
                VitalCardWidget(
                  title: 'BLOOD OXYGEN',
                  value: '${_vitals.spo2.round()}',
                  unit: '%',
                  normalRange: '95 - 100%',
                  status: _vitals.spo2 >= 95 ? 'OPTIMAL' : _vitals.spo2 >= 90 ? 'WARNING' : 'CRITICAL',
                  statusColor: _vitals.spo2 >= 95 ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                  icon: Icons.water_drop,
                ),
                VitalCardWidget(
                  title: 'HEART RATE',
                  value: '${_vitals.bpm.round()}',
                  unit: 'BPM',
                  normalRange: '60 - 100',
                  status: _vitals.bpm > 100 ? 'TACHY' : _vitals.bpm < 50 ? 'BRADY' : 'NORMAL',
                  statusColor: (_vitals.bpm > 100 || _vitals.bpm < 50) ? const Color(0xFFF59E0B) : const Color(0xFF10B981),
                  icon: Icons.favorite,
                ),
                VitalCardWidget(
                  title: 'CORE TEMPERATURE',
                  value: _vitals.temp.toStringAsFixed(1),
                  unit: '°C',
                  normalRange: '36.5 - 37.5',
                  status: _vitals.temp >= 38.5 ? 'HIGH FEVER' : _vitals.temp >= 37.5 ? 'FEBRILE' : 'NORMAL',
                  statusColor: _vitals.temp >= 38.0 ? const Color(0xFFEF4444) : const Color(0xFF10B981),
                  icon: Icons.thermostat,
                ),
                VitalCardWidget(
                  title: 'PERFUSION INDEX',
                  value: _vitals.pi.toStringAsFixed(2),
                  unit: '%',
                  normalRange: '> 1.0%',
                  status: _vitals.pi >= 1.0 ? 'ADEQUATE' : 'WEAK PULSE',
                  statusColor: _vitals.pi >= 1.0 ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                  icon: Icons.waves,
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Thermal Heatmap
            ThermalHeatmapWidget(
              temp: _vitals.temp,
              asym: _vitals.asym,
              feverProb: _vitals.feverProb,
            ),
            const SizedBox(height: 12),

            // Multi-Spectral AS7343 & HRV card
            _buildSpectralCard(),
            const SizedBox(height: 16),

            // Referral Action Button
            ElevatedButton.icon(
              onPressed: _openReferral,
              icon: const Icon(Icons.assignment_turned_in, color: Colors.black),
              label: const Text(
                'GENERATE AYUSHMAN BHARAT SLIP',
                style: TextStyle(fontWeight: FontWeight.w800, color: Colors.black, letterSpacing: 0.5),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF00E5FF),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 4,
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: const Color(0xFF0F172A).withOpacity(0.95),
      elevation: 0,
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF00E5FF), Color(0xFF6366F1)]),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.medical_services, size: 18, color: Colors.black),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text('Smart-ASHA', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF00E5FF))),
              Text('Offline Clinical Workstation', style: TextStyle(fontSize: 10, color: Colors.white54)),
            ],
          ),
        ],
      ),
      actions: [
        // Voice Language Toggle
        IconButton(
          tooltip: 'Toggle Hindi / English Audio Guidance',
          icon: Icon(
            widget.audioService.language == AudioLanguage.hindi
                ? Icons.record_voice_over
                : widget.audioService.language == AudioLanguage.english
                    ? Icons.voice_chat
                    : Icons.volume_off,
            color: const Color(0xFF00E5FF),
            size: 20,
          ),
          onPressed: () {
            setState(() {
              if (widget.audioService.language == AudioLanguage.hindi) {
                widget.audioService.setLanguage(AudioLanguage.english);
              } else if (widget.audioService.language == AudioLanguage.english) {
                widget.audioService.setLanguage(AudioLanguage.mute);
              } else {
                widget.audioService.setLanguage(AudioLanguage.hindi);
              }
            });
          },
        ),

        // History Log
        IconButton(
          tooltip: 'Offline Screening Log',
          icon: const Icon(Icons.history, color: Colors.white70, size: 20),
          onPressed: () {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const HistoryScreen()));
          },
        ),

        // Fail-Safe Simulator Toggle (Profile A / B / C)
        IconButton(
          tooltip: 'Demo Simulator Mode (Cycle Profile A / B / C)',
          icon: Icon(
            Icons.tune,
            color: widget.bleService.simMode > 0 ? const Color(0xFFF59E0B) : Colors.white70,
            size: 20,
          ),
          onPressed: () {
            widget.bleService.toggleSimulator();
            setState(() {});
          },
        ),
      ],
    );
  }

  Widget _buildConnectionBanner() {
    final isConnected = _connStatus == ConnectionStatus.connected;
    final isSim = _connStatus == ConnectionStatus.simulatorMode;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withOpacity(0.85),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isConnected ? const Color(0xFF10B981) : isSim ? const Color(0xFFF59E0B) : const Color(0xFF64748B),
                  boxShadow: isConnected
                      ? [const BoxShadow(color: Color(0xFF10B981), blurRadius: 6)]
                      : null,
                ),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isConnected ? 'BLE Connected' : isSim ? 'Demo Simulator' : 'Bluetooth Offline',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  Text(
                    widget.bleService.deviceName,
                    style: TextStyle(fontSize: 10, color: Colors.white.withOpacity(0.5), fontFamily: 'monospace'),
                  ),
                ],
              ),
            ],
          ),
          Row(
            children: [
              // Express mode button
              InkWell(
                onTap: _toggleExpressMode,
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: _isExpressMode ? const Color(0xFF00E5FF).withOpacity(0.2) : Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: _isExpressMode ? const Color(0xFF00E5FF) : Colors.white12),
                  ),
                  child: Text(
                    _isExpressMode ? '⚡ 10s' : '⏱️ 60s',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: _isExpressMode ? const Color(0xFF00E5FF) : Colors.white70,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),

              // BLE Connect / Scan Button
              ElevatedButton.icon(
                onPressed: () async {
                  try {
                    await widget.bleService.startScan();
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(e.toString())),
                    );
                  }
                },
                icon: Icon(
                  isConnected ? Icons.bluetooth_connected : Icons.bluetooth,
                  size: 14,
                  color: Colors.white,
                ),
                label: Text(
                  isConnected ? 'Disconnect' : _connStatus == ConnectionStatus.scanning ? 'Scanning...' : 'Pair BLE',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: isConnected ? const Color(0xFFEF4444).withOpacity(0.8) : const Color(0xFF2563EB),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSpectralCard() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withOpacity(0.85),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.biotech, size: 16, color: Color(0xFF6366F1)),
              SizedBox(width: 6),
              Text(
                'AS7343 MULTI-SPECTRAL & HRV BIOMARKERS',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white70, letterSpacing: 0.5),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _subMetric('Hb Optical Ratio', _vitals.hb.toStringAsFixed(2), _vitals.hb < 0.65 ? 'Severe Pallor' : 'Normal', _vitals.hb < 0.65 ? const Color(0xFFEF4444) : const Color(0xFF10B981)),
              _subMetric('Jaundice Index', _vitals.jaund.toStringAsFixed(2), _vitals.jaund > 1.4 ? 'Bilirubin High' : 'Normal', _vitals.jaund > 1.4 ? const Color(0xFFF59E0B) : const Color(0xFF10B981)),
              _subMetric('Hydration Index', _vitals.dehy.toStringAsFixed(2), _vitals.dehy > 1.3 ? 'Dehydrated' : 'Hydrated', _vitals.dehy > 1.3 ? const Color(0xFFF59E0B) : const Color(0xFF10B981)),
              _subMetric('SDNN (HRV)', '${_vitals.sdnn.toStringAsFixed(0)} ms', _vitals.sdnn < 20 ? 'Suppressed' : 'Healthy', _vitals.sdnn < 20 ? const Color(0xFFEF4444) : const Color(0xFF10B981)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _subMetric(String label, String val, String status, Color statusColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 9, color: Colors.white.withOpacity(0.4))),
        const SizedBox(height: 2),
        Text(val, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white, fontFamily: 'monospace')),
        const SizedBox(height: 2),
        Text(status, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w600, color: statusColor)),
      ],
    );
  }
}
