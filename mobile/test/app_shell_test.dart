import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/features/shell/presentation/app_shell.dart';

void main() {
  testWidgets('shell starts on dashboard', (tester) async {
    await tester.pumpWidget(
      MaterialApp(home: AppShell(email: 'test@example.com', onLogout: () async {})),
    );

    expect(find.text('Money Maintainer'), findsOneWidget);
    expect(find.text('Your money at a glance'), findsOneWidget);
  });

  testWidgets('shell navigation opens profile', (tester) async {
    await tester.pumpWidget(
      MaterialApp(home: AppShell(email: 'test@example.com', onLogout: () async {})),
    );

    await tester.tap(find.text('Profile'));
    await tester.pump();

    expect(find.text('test@example.com'), findsOneWidget);
    expect(find.text('test@example.com'), findsOneWidget);
  });
}
