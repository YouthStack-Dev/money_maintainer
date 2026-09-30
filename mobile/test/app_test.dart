import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:money_maintainer/app.dart';
import 'package:money_maintainer/features/auth/auth_gate.dart';
import 'package:money_maintainer/features/home/home_screen.dart';

void main() {
  testWidgets('Money Maintainer renders authentication gate', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());
    expect(find.byType(AuthGate), findsOneWidget);
  });

  testWidgets('home exposes logout action and confirmation dialog', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: HomeScreen()));
    expect(find.byTooltip('Log out'), findsOneWidget);
    await tester.tap(find.byTooltip('Log out'));
    await tester.pump();
    expect(find.text('Log out?'), findsOneWidget);
    expect(find.text('Cancel'), findsOneWidget);
    expect(find.widgetWithText(FilledButton, 'Log out'), findsOneWidget);
  });
}
