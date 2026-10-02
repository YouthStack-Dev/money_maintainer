import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/app/app.dart';

void main() {
  testWidgets('foundation app starts at auth gate', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());

    expect(find.text('Continue to app'), findsOneWidget);
  });
}
