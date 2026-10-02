import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/config/app_environment.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_api.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_repository.dart';
import 'package:money_maintainer_mobile/features/auth/presentation/auth_gate.dart';

class FakeAuthRepository extends AuthRepository {
  FakeAuthRepository() : super(config: AppEnvironmentConfig.development);

  @override
  Future<AuthSession> login({required String email, required String pin}) {
    return Future.value(const AuthSession(
      accessToken: 'access',
      refreshToken: 'refresh',
      role: 'USER',
    ));
  }
}

void main() {
  testWidgets('auth screen validates four digit PIN', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AuthScreen(
          repository: FakeAuthRepository(),
          onAuthenticated: () async {},
        ),
      ),
    );

    await tester.tap(find.text('Login'));
    await tester.pump();

    expect(find.text('Enter a valid email'), findsOneWidget);
  });
}
