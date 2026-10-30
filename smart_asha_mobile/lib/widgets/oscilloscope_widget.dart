import 'dart:math' as math;
import 'package:flutter/material.dart';

class OscilloscopeWidget extends StatefulWidget {
  final double bpm;
  final bool isScanning;

  const OscilloscopeWidget({
    Key? key,
    required this.bpm,
    this.isScanning = false,
  }) : super(key: key);

  @override
  State<OscilloscopeWidget> createState() => _OscilloscopeWidgetState();
}

class _OscilloscopeWidgetState extends State<OscilloscopeWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 180,
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withOpacity(0.85),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          AnimatedBuilder(
            animation: _controller,
            builder: (context, _) {
              return CustomPaint(
                size: Size.infinite,
                painter: _ScopePainter(
                  progress: _controller.value,
                  bpm: widget.bpm,
                  isScanning: widget.isScanning,
                ),
              );
            },
          ),
          Positioned(
            top: 10,
            left: 14,
            child: Row(
              children: [
                _buildChannelBadge('CH1 PPG (IR)', const Color(0xFF10B981)),
                const SizedBox(width: 8),
                _buildChannelBadge('CH2 ECG Lead I', const Color(0xFF00E5FF)),
              ],
            ),
          ),
          Positioned(
            top: 10,
            right: 14,
            child: Text(
              '60 FPS • 250 Hz',
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 10,
                color: Colors.white.withOpacity(0.4),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChannelBadge(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: [BoxShadow(color: color.withOpacity(0.6), blurRadius: 6)],
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(
            color: color,
            fontSize: 11,
            fontWeight: FontWeight.w600,
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }
}

class _ScopePainter extends CustomPainter {
  final double progress;
  final double bpm;
  final bool isScanning;

  _ScopePainter({
    required this.progress,
    required this.bpm,
    required this.isScanning,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Draw Grid
    final gridPaint = Paint()
      ..color = Colors.white.withOpacity(0.04)
      ..strokeWidth = 1.0;

    const step = 20.0;
    for (double x = 0; x < w; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, h), gridPaint);
    }
    for (double y = 0; y < h; y += step) {
      canvas.drawLine(Offset(0, y), Offset(w, y), gridPaint);
    }

    final t = progress * math.pi * 8;
    final rateFactor = (bpm / 60.0).clamp(0.8, 2.2);

    // Channel 1: PPG Waveform (Neon Green, top half)
    final ppgPaint = Paint()
      ..color = const Color(0xFF10B981)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    final ppgPath = Path();
    final ppgBaseY = h * 0.32;

    for (double x = 0; x < w; x += 3) {
      final phase = (x / w) * math.pi * 6 * rateFactor - t;
      // Dicrotic notch synthesis
      final primary = math.sin(phase);
      final notch = 0.35 * math.sin(phase * 2 + 1.2);
      final y = ppgBaseY - (primary + notch) * 26.0;

      if (x == 0) {
        ppgPath.moveTo(x, y);
      } else {
        ppgPath.lineTo(x, y);
      }
    }
    canvas.drawPath(ppgPath, ppgPaint);

    // Channel 2: ECG Lead I Waveform (Electric Cyan, bottom half)
    final ecgPaint = Paint()
      ..color = const Color(0xFF00E5FF)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    final ecgPath = Path();
    final ecgBaseY = h * 0.72;

    for (double x = 0; x < w; x += 3) {
      final phase = ((x / w) * 6 * rateFactor - t / math.pi) % 1.0;
      double offset = 0.0;

      // P wave
      if (phase > 0.1 && phase < 0.2) {
        offset = math.sin((phase - 0.1) / 0.1 * math.pi) * 8.0;
      }
      // Q dip
      else if (phase >= 0.2 && phase < 0.24) {
        offset = -4.0;
      }
      // R spike
      else if (phase >= 0.24 && phase < 0.29) {
        offset = 42.0 * math.sin((phase - 0.24) / 0.05 * math.pi);
      }
      // S dip
      else if (phase >= 0.29 && phase < 0.34) {
        offset = -12.0 * math.sin((phase - 0.29) / 0.05 * math.pi);
      }
      // T wave
      else if (phase >= 0.42 && phase < 0.58) {
        offset = 12.0 * math.sin((phase - 0.42) / 0.16 * math.pi);
      }

      final y = ecgBaseY - offset;

      if (x == 0) {
        ecgPath.moveTo(x, y);
      } else {
        ecgPath.lineTo(x, y);
      }
    }
    canvas.drawPath(ecgPath, ecgPaint);

    // Sweep cursor line
    final cursorX = (progress * w) % w;
    final cursorPaint = Paint()
      ..color = const Color(0xFF00E5FF).withOpacity(0.4)
      ..strokeWidth = 2.0;
    canvas.drawLine(Offset(cursorX, 0), Offset(cursorX, h), cursorPaint);
  }

  @override
  bool shouldRepaint(covariant _ScopePainter oldDelegate) => true;
}
