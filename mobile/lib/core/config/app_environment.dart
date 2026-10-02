enum AppEnvironment { development, staging, production }

class AppEnvironmentConfig {
  const AppEnvironmentConfig({
    required this.environment,
    required this.apiBaseUrl,
  });

  final AppEnvironment environment;
  final String apiBaseUrl;

  static const development = AppEnvironmentConfig(
    environment: AppEnvironment.development,
    apiBaseUrl: 'http://10.0.2.2:8000',
  );

  static const staging = AppEnvironmentConfig(
    environment: AppEnvironment.staging,
    apiBaseUrl: String.fromEnvironment('MM_STAGING_API_URL'),
  );

  static const production = AppEnvironmentConfig(
    environment: AppEnvironment.production,
    apiBaseUrl: String.fromEnvironment('MM_PRODUCTION_API_URL'),
  );
}
