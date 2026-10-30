import 'dart:math' as math;
import 'package:flutter/material.dart';

class ThermalHeatmapWidget extends StatelessWidget {
  final double temp;
  final double asym;
  final int feverProb;

  const ThermalHeatmapWidget({
    Key? key,
    required this.temp,
    required this.asym,
    required this.feverProb,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
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
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Color(0xFFF59E0B),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'MLX90640 THERMAL ARRAY (24×32)',
                    style: TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Colors.white70,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: feverProb > 50
                      ? const Color(0xFFEF4444).withOpacity(0.2)
                      : const Color(0xFF10B981).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: feverProb > 50
                        ? const Color(0xFFEF4444)
                        : const Color(0xFF10B981),
                  ),
                ),
                child: Text(
                  'Fever Prob: $feverProb%',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: feverProb > 50
                        ? const Color(0xFFEF4444)
                        : const Color(0xFF10B981),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: SizedBox(
              height: 160,
              width: double.infinity,
              child: CustomPaint(
                painter: _ThermalPainter(temp: temp, asym: asym),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricBadge('Max Temp', '${temp.toStringAsFixed(1)}°C', const Color(0xFFEF4444)),
              _metricBadge('Ambient', '26.8°C', const Color(0xFF64748B)),
              _metricBadge('Asymmetry', 'Δ ${(asym * 10).toStringAsFixed(1)}°C', const Color(0xFFF59E0B)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricBadge(String label, String val, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 10, color: Colors.white.withOpacity(0.5))),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: color, fontFamily: 'monospace')),
      ],
    );
  }
}

class _ThermalPainter extends CustomPainter {
  final double temp;
  final double asym;

  _ThermalPainter({required this.temp, required this.asym});

  static const int cols = 32;
  static const int rows = 24;

  @override
  void paint(Canvas canvas, Size size) {
    final cellW = size.width / cols;
    final cellH = size.height / rows;

    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        // Synthesize realistic biological thermal face distribution
        final dx = (c - cols / 2.0) / (cols / 2.0);
        final dy = (r - rows / 2.0) / (rows / 2.0);
        final dist = math.sqrt(dx * dx + dy * dy);

        double localTemp = 24.0; // background ambient

        if (dist < 0.95) {
          // Face ellipse
          localTemp = 33.0 + (temp - 36.6) * 0.8;

          // Forehead hotspot (top center)
          if (dy < -0.1 && dy > -0.65 && dx.abs() < 0.5) {
            localTemp += 2.8 + (temp > 38 ? 1.5 : 0);
          }
          // Inner canthi (eyes)
          if (dy.abs() < 0.15 && dx.abs() < 0.35 && dx.abs() > 0.1) {
            localTemp += 2.2;
          }
          // Asymmetry shift
          if (dx > 0) {
            localTemp += asym * 1.5;
          }
        }

        final color = _getIronbowColor(localTemp);
        final paint = Paint()..color = color;
        canvas.drawRect(
          Rect.fromLTWH(c * cellW, r * cellH, cellW + 0.5, cellH + 0.5),
          paint,
        );
      }
    }
  }

  /// High-contrast medical Ironbow colormap
  Color _getIronbowColor(double t) {
    final norm = ((t - 22.0) / 19.0).clamp(0.0, 1.0);
    if (norm < 0.2) {
      return Color.lerp(const Color(0xFF0B0F19), const Color(0xFF3B0764), norm / 0.2)!;
    } else if (norm < 0.4) {
      return Color.lerp(const Color(0xFF3B0764), const Color(0xFF1D4ED8), (norm - 0.2) / 0.2)!;
    } else if (norm < 0.6) {
      return Color.lerp(const Color(0xFF1D4ED8), const Color(0xFF10B981), (norm - 0.4) / 0.2)!;
    } else if (norm < 0.8) {
      return Color.lerp(const Color(0xFF10B981), const Color(0xFFF59E0B), (norm - 0.6) / 0.2)!;
    } else {
      return Color.lerp(const Color(0xFFF59E0B), const Color(0xFFEF4444), (norm - 0.8) / 0.2)!;
    }
  }

  @override
  bool shouldRepaint(covariant _ThermalPainter oldDelegate) {
    return oldDelegate.temp != temp || oldDelegate.asym != asym;
  }
}
