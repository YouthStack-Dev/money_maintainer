import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/features/auth/presentation/auth_gate.dart';

void main() {
  testWidgets('auth screen requires a four digit PIN', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AuthScreen(
          repository: throw UnimplementedError(),
          onAuthenticated: () {},
        ),
      ),
    );
  });
}
