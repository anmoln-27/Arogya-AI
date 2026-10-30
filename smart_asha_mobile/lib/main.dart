import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/ble_service.dart';
import 'services/audio_guidance_service.dart';
import 'screens/dashboard_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set immersive dark status bar
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Color(0xFF0B0F19),
    systemNavigationBarIconBrightness: Brightness.light,
  ));

  // Instantiate singleton services
  final bleService = BleService();
  final audioService = AudioGuidanceService();
  await audioService.init();

  runApp(SmartAshaApp(
    bleService: bleService,
    audioService: audioService,
  ));
}

class SmartAshaApp extends StatelessWidget {
  final BleService bleService;
  final AudioGuidanceService audioService;

  const SmartAshaApp({
    Key? key,
    required this.bleService,
    required this.audioService,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart-ASHA Clinical Workstation',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0B0F19),
        primaryColor: const Color(0xFF00E5FF),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00E5FF),
          secondary: Color(0xFF6366F1),
          surface: Color(0xFF0F172A),
          error: Color(0xFFEF4444),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0F172A),
          elevation: 0,
        ),
      ),
      home: DashboardScreen(
        bleService: bleService,
        audioService: audioService,
      ),
    );
  }
}
