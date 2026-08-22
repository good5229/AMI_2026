import 'package:flutter/material.dart';

class AppTheme {
  static const ink = Color(0xFF102A43);
  static const canvas = Color(0xFFF4F1EA);
  static const paper = Color(0xFFFFFDF8);
  static const signal = Color(0xFF0F766E);
  static const caution = Color(0xFFD97706);
  static const line = Color(0xFFD8D4CA);

  static ThemeData light() {
    const scheme = ColorScheme.light(
      primary: ink,
      onPrimary: Colors.white,
      secondary: signal,
      onSecondary: Colors.white,
      error: Color(0xFFB42318),
      onError: Colors.white,
      surface: paper,
      onSurface: ink,
      outline: line,
    );
    final textTheme = Typography.material2021().black.apply(
          bodyColor: ink,
          displayColor: ink,
          fontFamily: 'Noto Sans KR',
          fontFamilyFallback: const ['Apple SD Gothic Neo', 'sans-serif'],
        );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: canvas,
      textTheme: textTheme.copyWith(
        headlineLarge: textTheme.headlineLarge?.copyWith(
          fontWeight: FontWeight.w800,
          height: 1.12,
          letterSpacing: -0.8,
        ),
        headlineSmall: textTheme.headlineSmall?.copyWith(
          fontWeight: FontWeight.w800,
          height: 1.2,
          letterSpacing: -0.35,
        ),
        titleLarge: textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.w800,
          letterSpacing: -0.2,
        ),
        titleMedium:
            textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
        bodyLarge: textTheme.bodyLarge?.copyWith(height: 1.55),
        bodyMedium: textTheme.bodyMedium?.copyWith(height: 1.5),
        labelLarge:
            textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
      ),
      appBarTheme: const AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
        foregroundColor: ink,
        backgroundColor: paper,
        surfaceTintColor: Colors.transparent,
      ),
      cardTheme: const CardThemeData(
        color: paper,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        margin: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(18)),
          side: BorderSide(color: line),
        ),
      ),
      dividerTheme: const DividerThemeData(color: line, thickness: 1),
      chipTheme: ChipThemeData(
        backgroundColor: const Color(0xFFE7F2EF),
        side: BorderSide.none,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        labelStyle:
            const TextStyle(color: ink, fontWeight: FontWeight.w700),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: paper,
        indicatorColor: const Color(0xFFD5EAE5),
        elevation: 0,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => TextStyle(
            color: ink,
            fontSize: 11,
            fontWeight: states.contains(WidgetState.selected)
                ? FontWeight.w800
                : FontWeight.w600,
          ),
        ),
      ),
      navigationRailTheme: const NavigationRailThemeData(
        backgroundColor: paper,
        indicatorColor: Color(0xFFD5EAE5),
        selectedIconTheme: IconThemeData(color: signal),
        selectedLabelTextStyle:
            TextStyle(color: ink, fontWeight: FontWeight.w800),
        unselectedLabelTextStyle: TextStyle(color: Color(0xFF52606D)),
      ),
    );
  }
}
