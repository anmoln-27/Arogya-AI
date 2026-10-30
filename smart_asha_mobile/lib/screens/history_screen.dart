import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import '../services/storage_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<ScreeningRecord> _records = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final data = await StorageService.getRecords();
    setState(() {
      _records = data;
      _loading = false;
    });
  }

  Future<void> _exportCsv() async {
    if (_records.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No records to export.')),
      );
      return;
    }
    final csv = await StorageService.generateCsv();
    await Share.share(csv, subject: 'Smart_ASHA_Offline_Screenings.csv');
  }

  Future<void> _clearAll() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Clear All Screenings?', style: TextStyle(color: Colors.white)),
        content: const Text('This will delete all offline records from this phone.', style: TextStyle(color: Colors.white70)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete', style: TextStyle(color: Color(0xFFEF4444))),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await StorageService.clearAll();
      _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0F19),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Offline Screening Log', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.file_download, color: Color(0xFF00E5FF)),
            tooltip: 'Export CSV',
            onPressed: _exportCsv,
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Colors.white60),
            tooltip: 'Clear Log',
            onPressed: _records.isEmpty ? null : _clearAll,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF00E5FF)))
          : _records.isEmpty
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.inventory_2_outlined, size: 48, color: Colors.white.withOpacity(0.3)),
                      const SizedBox(height: 12),
                      Text('No screenings recorded yet', style: TextStyle(color: Colors.white.withOpacity(0.6))),
                      const SizedBox(height: 6),
                      Text('Saved screenings will appear here offline', style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.35))),
                    ],
                  ),
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _records.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 10),
                  itemBuilder: (ctx, i) {
                    final r = _records[i];
                    final color = r.triage == 'RED'
                        ? const Color(0xFFEF4444)
                        : r.triage == 'YELLOW'
                            ? const Color(0xFFF59E0B)
                            : const Color(0xFF10B981);

                    return Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.white.withOpacity(0.06)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                r.patientName,
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: color.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(color: color, width: 1),
                                ),
                                child: Text(
                                  r.triage,
                                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${r.timestamp} • ${r.village}',
                            style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.4)),
                          ),
                          const SizedBox(height: 10),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              _chip('SpO₂', '${r.spo2.round()}%'),
                              _chip('Pulse', '${r.bpm.round()} BPM'),
                              _chip('Temp', '${r.temp.toStringAsFixed(1)}°C'),
                              _chip('Score', '${r.score}/100'),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }

  Widget _chip(String label, String val) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.04),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('$label: ', style: TextStyle(fontSize: 10, color: Colors.white.withOpacity(0.4))),
          Text(val, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white, fontFamily: 'monospace')),
        ],
      ),
    );
  }
}
