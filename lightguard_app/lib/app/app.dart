import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/constants/app_strings.dart';
import 'router/app_router.dart';
import 'theme/app_theme.dart';

class LightguardApp extends ConsumerStatefulWidget {
  const LightguardApp({super.key});

  @override
  ConsumerState<LightguardApp> createState() => _LightguardAppState();
}

class _LightguardAppState extends ConsumerState<LightguardApp> {
  late final router = createRouter();

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: AppStrings.appTitle,
      theme: AppTheme.light(),
      routerConfig: router,
    );
  }
}
