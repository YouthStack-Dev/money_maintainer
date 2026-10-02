import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/utils/result.dart';

void main() {
  test('Success contains a value', () {
    const result = Success<String>('ok');

    expect(result.isSuccess, isTrue);
    expect(result.value, 'ok');
  });

  test('Failure contains an error', () {
    final result = Failure<String>(Exception('failed'));

    expect(result.isSuccess, isFalse);
    expect(result.error, isA<Exception>());
  });
}
