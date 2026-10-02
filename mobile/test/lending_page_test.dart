import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:money_maintainer_mobile/features/lending/presentation/lending_page.dart';

void main() {
  testWidgets('lending page renders', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: LendingPage(accessToken: '')),
    );
    expect(find.text('Lending'), findsOneWidget);
  });
}
