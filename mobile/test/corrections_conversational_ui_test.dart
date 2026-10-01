import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:money_maintainer/features/corrections/correction_screen.dart';
import 'package:money_maintainer/features/conversational_finance/conversational_finance_screen.dart';

void main() {
  testWidgets('correction screen exposes local input validation',
      (tester) async {
    await tester.pumpWidget(const MaterialApp(home: CorrectionScreen()));
    await tester.tap(find.text('Review correction'));
    await tester.pump();
    expect(find.text('What should be corrected?'), findsOneWidget);
    expect(find.text('Review correction'), findsOneWidget);
  });

  testWidgets('finance assistant exposes question input', (tester) async {
    await tester
        .pumpWidget(const MaterialApp(home: ConversationalFinanceScreen()));
    expect(find.text('Finance assistant'), findsOneWidget);
    expect(find.text('Ask your finance question'), findsOneWidget);
  });
}
