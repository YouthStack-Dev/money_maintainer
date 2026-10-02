import 'package:flutter/material.dart';

import '../features/auth/presentation/auth_gate.dart';
import 'app_theme.dart';

class MoneyMaintainerApp extends StatelessWidget {
  const MoneyMaintainerApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Money Maintainer',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.light(),
    home: const AuthGate(),
  );
}
