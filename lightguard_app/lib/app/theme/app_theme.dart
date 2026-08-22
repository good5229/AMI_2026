import 'package:flutter/material.dart';

class AppTheme {
  static const ink = Color(0xFF102A43);
  static const canvas = Color(0xFFF5F6F2);
  static const paper = Color(0xFFFFFEFB);
  static const surfaceMuted = Color(0xFFF0F3EF);
  static const textMuted = Color(0xFF5C6B73);
  static const signal = Color(0xFF0F766E);
  static const caution = Color(0xFFD97706);
  static const line = Color(0xFFDDE2DD);

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
        toolbarHeight: 68,
        titleSpacing: 20,
        foregroundColor: ink,
        backgroundColor: paper,
        surfaceTintColor: Colors.transparent,
      ),
      cardTheme: const CardThemeData(
        color: paper,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shadowColor: Color(0x12102A43),
        margin: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(14)),
          side: BorderSide(color: line),
        ),
      ),
      dividerTheme: const DividerThemeData(color: line, thickness: 1),
      chipTheme: ChipThemeData(
        backgroundColor: surfaceMuted,
        side: const BorderSide(color: line),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        labelStyle:
            const TextStyle(color: ink, fontWeight: FontWeight.w600),
        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 4),
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
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: paper,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: line),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: line),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: signal, width: 2),
        ),
      ),
      listTileTheme: const ListTileThemeData(
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 2),
        iconColor: ink,
      ),
      expansionTileTheme: const ExpansionTileThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.zero),
        collapsedShape: RoundedRectangleBorder(borderRadius: BorderRadius.zero),
        iconColor: signal,
        collapsedIconColor: ink,
      ),
    );
  }
}
