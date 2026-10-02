import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/config/app_environment.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_api.dart';
import 'package:money_maintainer_mobile/features/auth/data/auth_repository.dart';
import 'package:money_maintainer_mobile/features/profile/presentation/profile_page.dart';

class FakeProfileRepository extends AuthRepository {
  FakeProfileRepository() : super(config: AppEnvironmentConfig.development);

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
  testWidgets('profile renders current user details', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ProfilePage(
          repository: FakeProfileRepository(),
          onLogout: () async {},
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Test User'), findsOneWidget);
    expect(find.text('test@example.com'), findsNWidgets(2));
    expect(find.text('Verified'), findsOneWidget);
  });
}
