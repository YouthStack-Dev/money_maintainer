import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer/core/network/api_client.dart';
import 'package:money_maintainer/features/auth/login_screen.dart';
import 'package:money_maintainer/features/auth/register_screen.dart';

void main() {
  test('ApiException maps common backend status codes', () {
    expect(
      const ApiException(401, {'detail': 'Invalid credentials'}).userMessage,
      'Authentication failed. Please sign in again.',
    );
    expect(
      const ApiException(409, {'detail': 'Email already registered'})
          .userMessage,
      'Email already registered',
    );
    expect(
      const ApiException(429, {'detail': 'Too many failed login attempts'})
          .userMessage,
      'Too many failed login attempts',
    );
    expect(
      const ApiException(500, null).userMessage,
      'The server is temporarily unavailable. Please try again later.',
    );
  });

  testWidgets('login password visibility can be toggled', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: LoginScreen(
          onLoggedIn: () {},
          onRegister: () {},
        ),
      ),
    );

    expect(find.byIcon(Icons.visibility_outlined), findsOneWidget);
    expect(find.text('I have a reset token'), findsNothing);
    expect(find.text('Verify email'), findsNothing);
    await tester.tap(find.byIcon(Icons.visibility_outlined));
    await tester.pump();
    expect(find.byIcon(Icons.visibility_off_outlined), findsOneWidget);
  });

  testWidgets('register validates password length before API call',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: RegisterScreen(
          onRegistered: () {},
          onBackToLogin: () {},
        ),
      ),
    );

    await tester.enterText(find.byType(TextField).at(0), 'Test User');
    await tester.enterText(find.byType(TextField).at(1), 'test@example.com');
    await tester.enterText(find.byType(TextField).at(2), 'short');
    await tester.enterText(find.byType(TextField).at(3), 'short');

    await tester.tap(find.widgetWithText(FilledButton, 'Create account'));
    await tester.pump();

    expect(find.text('Password must be 12-128 characters.'), findsOneWidget);
  });
}
