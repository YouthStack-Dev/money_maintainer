import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/app/app.dart';

void main() {
  testWidgets('foundation app starts', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());

    expect(find.text('Money Maintainer'), findsOneWidget);
  });
}
