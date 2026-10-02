import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/config/app_environment.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_api.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_repository.dart';
import 'package:money_maintainer_mobile/features/shell/presentation/app_shell.dart';

class FakeShellRepository extends AuthRepository {
  FakeShellRepository() : super(config: AppEnvironmentConfig.development);

  @override
  Future<String> get accessToken async => '';

  @override
  Future<CurrentUser> currentUser() async => const CurrentUser(
        id: 1,
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'USER',
        isEmailVerified: true,
      );
}

void main() {
  testWidgets('shell starts on dashboard', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AppShell(
          repository: FakeShellRepository(),
          accessToken: '',
          email: 'test@example.com',
          onLogout: () async {},
        ),
      ),
    );

    await tester.pump();
    expect(find.text('Money Maintainer'), findsOneWidget);
    expect(find.text('Your money at a glance'), findsOneWidget);
  });

  testWidgets('shell navigation opens profile', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AppShell(
          repository: FakeShellRepository(),
          accessToken: '',
          email: 'test@example.com',
          onLogout: () async {},
        ),
      ),
    );

    await tester.tap(find.text('Profile'));
    await tester.pump();

    expect(find.text('test@example.com'), findsOneWidget);
  });
}
