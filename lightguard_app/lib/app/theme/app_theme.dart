import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData light() {
    final base = ColorScheme.fromSeed(seedColor: const Color(0xFF1A4B7B));
    return ThemeData(
      useMaterial3: true,
      colorScheme: base,
      scaffoldBackgroundColor: const Color(0xFFF5F7FB),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        foregroundColor: Colors.white,
        backgroundColor: Color(0xFF1A4B7B),
      ),
      cardTheme: const CardThemeData(
        elevation: 2,
        margin: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
    );
  }
}
