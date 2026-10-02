import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/config/app_environment.dart';

void main() {
  test('development environment has a valid API URL', () {
    const config = AppEnvironmentConfig.development;

    expect(config.environment, AppEnvironment.development);
    expect(Uri.tryParse(config.apiBaseUrl), isNotNull);
  });
}
