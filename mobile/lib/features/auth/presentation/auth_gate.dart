import 'package:flutter/material.dart';

import '../../shell/presentation/app_shell.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return const _AuthPlaceholder();
  }
}

class _AuthPlaceholder extends StatelessWidget {
  const _AuthPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: FilledButton(
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute<void>(builder: (_) => const AppShell()),
              );
            },
            child: const Text('Continue to app'),
          ),
        ),
      ),
    );
  }
}
