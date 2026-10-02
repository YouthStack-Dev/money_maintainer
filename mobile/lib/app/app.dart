import 'package:flutter/material.dart';

import 'app_theme.dart';

class MoneyMaintainerApp extends StatelessWidget {
  const MoneyMaintainerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Money Maintainer',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      home: const _FoundationScreen(),
    );
  }
}

class _FoundationScreen extends StatelessWidget {
  const _FoundationScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Text('Money Maintainer'),
      ),
    );
  }
}
