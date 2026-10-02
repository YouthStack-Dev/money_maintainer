import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/app/app.dart';

void main() {
  testWidgets('app starts at the unauthenticated gate', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());

    expect(find.text('Continue to app'), findsOneWidget);
  });

  testWidgets('shell navigation changes destinations', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());
    await tester.tap(find.text('Continue to app'));
    await tester.pumpAndSettle();

    expect(find.text('Dashboard'), findsOneWidget);

    await tester.tap(find.text('Money'));
    await tester.pump();

    expect(find.text('Money'), findsOneWidget);
  });
}
