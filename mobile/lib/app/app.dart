import 'package:flutter/material.dart';

import '../features/auth/presentation/auth_gate.dart';
import 'app_theme.dart';

class MoneyMaintainerApp extends StatelessWidget {
  const MoneyMaintainerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Money Maintainer',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      routes: {
        AppRoutes.auth: (_) => const AuthGate(),
      },
      initialRoute: AppRoutes.auth,
    );
  }
}

abstract final class AppRoutes {
  static const auth = '/auth';
}
