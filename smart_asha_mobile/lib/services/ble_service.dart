import 'dart:async';
import 'dart:convert';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import '../models/vitals_model.dart';

enum ConnectionStatus {
  disconnected,
  scanning,
  connecting,
  connected,
  simulatorMode,
}

class BleService {
  static final Guid serviceUuid = Guid('4fafc201-1fb5-459e-8fcc-c5c9c331914b');
  static final Guid charUuid    = Guid('beb5483e-36e1-4688-b7f5-ea07361b26a8');

  BluetoothDevice? _device;
  BluetoothCharacteristic? _telemetryChar;
  StreamSubscription? _scanSub;
  StreamSubscription? _charSub;
  StreamSubscription? _connectionSub;

  final _vitalsController = StreamController<VitalsModel>.broadcast();
  Stream<VitalsModel> get vitalsStream => _vitalsController.stream;

  final _statusController = StreamController<ConnectionStatus>.broadcast();
  Stream<ConnectionStatus> get statusStream => _statusController.stream;

  ConnectionStatus _status = ConnectionStatus.disconnected;
  ConnectionStatus get status => _status;

  String _deviceName = 'Not Connected';
  String get deviceName => _deviceName;

  String _rxBuffer = '';
  int _simMode = 0; // 0=off, 1=A, 2=B, 3=C
  Timer? _simTimer;

  BleService() {
    _statusController.add(_status);
  }

  /// Start scanning for Smart-ASHA-Pro ESP32-S3 device
  Future<void> startScan() async {
    if (_status == ConnectionStatus.connected) {
      await disconnect();
      return;
    }

    // Check Bluetooth availability
    final adapterState = await FlutterBluePlus.adapterState.first;
    if (adapterState != BluetoothAdapterState.on) {
      throw Exception('Please enable Bluetooth on your phone.');
    }

    _setStatus(ConnectionStatus.scanning);

    try {
      await FlutterBluePlus.startScan(
        withServices: [serviceUuid],
        timeout: const Duration(seconds: 10),
      );

      _scanSub?.cancel();
      _scanSub = FlutterBluePlus.scanResults.listen((results) async {
        for (ScanResult r in results) {
          final name = r.device.platformName;
          if (name.contains('Smart-ASHA') || name.startsWith('Smart')) {
            await FlutterBluePlus.stopScan();
            await connect(r.device);
            break;
          }
        }
      });
    } catch (e) {
      _setStatus(ConnectionStatus.disconnected);
      rethrow;
    }
  }

  /// Connect to ESP32 device & setup GATT notifications
  Future<void> connect(BluetoothDevice device) async {
    _device = device;
    _setStatus(ConnectionStatus.connecting);

    try {
      await device.connect(autoConnect: false);
      _deviceName = device.platformName.isNotEmpty ? device.platformName : 'Smart-ASHA-Pro';

      // Monitor disconnect
      _connectionSub?.cancel();
      _connectionSub = device.connectionState.listen((state) {
        if (state == BluetoothConnectionState.disconnected) {
          _handleDisconnect();
        }
      });

      // Request larger MTU for faster JSON transfers
      try {
        await device.requestMtu(512);
      } catch (_) {}

      // Discover services
      final services = await device.discoverServices();
      for (var s in services) {
        if (s.uuid == serviceUuid) {
          for (var c in s.characteristics) {
            if (c.uuid == charUuid) {
              _telemetryChar = c;
              await c.setNotifyValue(true);
              _charSub?.cancel();
              _charSub = c.lastValueStream.listen(_onDataReceived);
              _setStatus(ConnectionStatus.connected);
              return;
            }
          }
        }
      }

      throw Exception('Smart-ASHA GATT Telemetry Service not found.');
    } catch (e) {
      _handleDisconnect();
      rethrow;
    }
  }

  /// Handle incoming BLE notification packets
  void _onDataReceived(List<int> bytes) {
    if (bytes.isEmpty || _simMode > 0) return;
    final chunk = utf8.decode(bytes, allowMalformed: true);

    // Direct single packet JSON
    if (chunk.startsWith('{') && chunk.endsWith('}')) {
      _tryParseJson(chunk);
      _rxBuffer = '';
      return;
    }

    _rxBuffer += chunk;
    if (_rxBuffer.startsWith('{') && _rxBuffer.endsWith('}')) {
      _tryParseJson(_rxBuffer);
      _rxBuffer = '';
    } else if (_rxBuffer.length > 2048) {
      _rxBuffer = ''; // Prevent buffer overflow on corrupt frame
    }
  }

  void _tryParseJson(String text) {
    try {
      final json = jsonDecode(text) as Map<String, dynamic>;
      final vitals = VitalsModel.fromJson(json);
      _vitalsController.add(vitals);
    } catch (_) {}
  }

  /// Send commands to ESP32: 'FAST', 'SLOW', 'SCAN', 'SLEEP'
  Future<void> sendCommand(String cmd) async {
    if (_telemetryChar != null && _status == ConnectionStatus.connected) {
      await _telemetryChar!.write(utf8.encode('$cmd\n'), withoutResponse: false);
    }
  }

  /// Disconnect active BLE session
  Future<void> disconnect() async {
    _scanSub?.cancel();
    _charSub?.cancel();
    _connectionSub?.cancel();
    if (_device != null) {
      await _device!.disconnect();
      _device = null;
    }
    _handleDisconnect();
  }

  void _handleDisconnect() {
    _telemetryChar = null;
    _deviceName = 'Not Connected';
    if (_simMode == 0) {
      _setStatus(ConnectionStatus.disconnected);
    }
  }

  void _setStatus(ConnectionStatus s) {
    _status = s;
    _statusController.add(s);
  }

  // ════════════ FAIL-SAFE OFFLINE SIMULATOR ════════════
  /// Cycles through simulator profiles for zero-hardware offline testing / judging
  void toggleSimulator() {
    _simTimer?.cancel();
    _simMode = (_simMode + 1) % 4; // 0=Off, 1=A, 2=B, 3=C

    if (_simMode == 0) {
      _setStatus(ConnectionStatus.disconnected);
      _vitalsController.add(VitalsModel());
      return;
    }

    _setStatus(ConnectionStatus.simulatorMode);
    _deviceName = 'Demo Simulator Profile ${_simMode == 1 ? "A (Healthy)" : _simMode == 2 ? "B (Febrile RED)" : "C (Cardiac YELLOW)"}';

    // Emit initial snapshot
    _emitSimulatorVitals();

    // Stream animated pulse values
    _simTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      _emitSimulatorVitals();
    });
  }

  void _emitSimulatorVitals() {
    if (_simMode == 1) {
      _vitalsController.add(VitalsModel.profileA());
    } else if (_simMode == 2) {
      _vitalsController.add(VitalsModel.profileB());
    } else if (_simMode == 3) {
      _vitalsController.add(VitalsModel.profileC());
    }
  }

  int get simMode => _simMode;

  void dispose() {
    _simTimer?.cancel();
    _scanSub?.cancel();
    _charSub?.cancel();
    _connectionSub?.cancel();
    _vitalsController.close();
    _statusController.close();
  }
}
