import 'package:flutter_test/flutter_test.dart';
import 'package:money_maintainer/app.dart';

void main() {
  testWidgets('Money Maintainer starts on Home', (tester) async {
    await tester.pumpWidget(const MoneyMaintainerApp());
    expect(find.text('Money Maintainer'), findsOneWidget);
    expect(find.text('Home'), findsOneWidget);
  });
}
