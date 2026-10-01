import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:money_maintainer/features/auth/change_password_screen.dart';
import 'package:money_maintainer/features/auth/forgot_password_screen.dart';
import 'package:money_maintainer/features/auth/reset_password_screen.dart';
import 'package:money_maintainer/features/auth/verify_email_screen.dart';

void main() {
  testWidgets('forgot password validates email locally', (tester) async {
    await tester
        .pumpWidget(MaterialApp(home: ForgotPasswordScreen(onBack: () {})));
    await tester.tap(find.text('Send reset email'));
    await tester.pump();
    expect(find.text('Enter a valid email address.'), findsOneWidget);
  });

  testWidgets('verify email validates empty token locally', (tester) async {
    await tester
        .pumpWidget(MaterialApp(home: VerifyEmailScreen(onBack: () {})));
    await tester.tap(find.widgetWithText(FilledButton, 'Verify email'));
    await tester.pump();
    expect(find.text('Verification token is required.'), findsOneWidget);
  });

  testWidgets('reset password validates token, length and confirmation',
      (tester) async {
    await tester
        .pumpWidget(MaterialApp(home: ResetPasswordScreen(onBack: () {})));
    await tester.tap(find.text('Reset password'));
    await tester.pump();
    expect(find.text('Reset token is required.'), findsOneWidget);
    await tester.enterText(find.byType(TextField).at(0), 'token');
    await tester.enterText(find.byType(TextField).at(1), 'short');
    await tester.enterText(find.byType(TextField).at(2), 'short');
    await tester.tap(find.text('Reset password'));
    await tester.pump();
    expect(find.text('Password must be 12-128 characters.'), findsOneWidget);
  });

  testWidgets('change password validates confirmation', (tester) async {
    await tester
        .pumpWidget(MaterialApp(home: ChangePasswordScreen(onChanged: () {})));
    await tester.enterText(find.byType(TextField).at(0), 'StrongPass123!');
    await tester.enterText(find.byType(TextField).at(1), 'DifferentPass123!');
    await tester.tap(find.widgetWithText(FilledButton, 'Change password'));
    await tester.pump();
    expect(find.text('Passwords do not match.'), findsOneWidget);
  });
}
