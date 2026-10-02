import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/core/config/app_environment.dart';
import 'package:money_maintainer_mobile/core/network/api_client.dart';

void main() {
  test('buildUri preserves base URL and appends path/query', () {
    const config = AppEnvironmentConfig(
      environment: AppEnvironment.staging,
      apiBaseUrl: 'https://example.com/api',
    );

    final uri = const ApiClient(config).buildUri(
      '/v1/auth/login',
      {'source': 'mobile'},
    );

    expect(uri.toString(), 'https://example.com/api/v1/auth/login?source=mobile');
  });
}
