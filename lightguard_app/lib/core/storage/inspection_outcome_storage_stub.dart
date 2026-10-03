import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';

const _channel = MethodChannel('kr.example.lightguard/local_cases');
Map<String, Map<String, String>> _memory = {};

Future<Map<String, Map<String, String>>> loadInspectionOutcomes() async {
  if (!Platform.isAndroid) {
    return _memory
        .map((key, value) => MapEntry(key, Map<String, String>.from(value)));
  }
  try {
    final raw = await _channel.invokeMethod<String>('load');
    if (raw != null && raw.isNotEmpty) {
      final decoded = jsonDecode(raw) as Map<String, dynamic>;
      return decoded.map((key, value) => MapEntry(
          key, Map<String, String>.from(value as Map<dynamic, dynamic>)));
    }
  } on MissingPluginException {
    rethrow;
  } catch (_) {
    return {};
  }
  return _memory
      .map((key, value) => MapEntry(key, Map<String, String>.from(value)));
}

Future<void> saveInspectionOutcomes(
    Map<String, Map<String, String>> outcomes) async {
  _memory = outcomes
      .map((key, value) => MapEntry(key, Map<String, String>.from(value)));
  if (!Platform.isAndroid) return;
  try {
    await _channel.invokeMethod<void>('save', jsonEncode(outcomes));
  } on MissingPluginException {
    rethrow;
  }
}
