import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/config/app_environment.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_api.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_repository.dart';
import 'package:money_maintainer_mobile/features/auth/presentation/auth_gate.dart';

class _FakeAuthRepository extends AuthRepository {
  _FakeAuthRepository() : super(config: AppEnvironmentConfig.development);

  @override
  Future<AuthSession> login({required String email, required String pin}) async =>
      const AuthSession(accessToken: 'a', refreshToken: 'r', role: 'USER');
}

void main() {
  testWidgets('auth screen is reachable', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AuthScreen(
          repository: _FakeAuthRepository(),
          onAuthenticated: () async {},
        ),
      ),
    );

    expect(find.text('Money Maintainer'), findsOneWidget);
    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('4-digit PIN'), findsOneWidget);
  });
}
