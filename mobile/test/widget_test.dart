import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/app/app.dart';

void main() {
  testWidgets('app reaches authentication screen', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());
    await tester.pumpAndSettle();

    expect(find.text('Money Maintainer'), findsOneWidget);
    expect(find.text('Welcome back'), findsOneWidget);
  });
}
