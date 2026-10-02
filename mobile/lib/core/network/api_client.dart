import '../config/app_environment.dart';

class ApiClient {
  const ApiClient(this.config);

  final AppEnvironmentConfig config;

  Uri buildUri(String path, [Map<String, dynamic>? queryParameters]) {
    final baseUri = Uri.parse(config.apiBaseUrl);
    final normalizedPath = path.startsWith('/') ? path : '/$path';

    return baseUri.replace(
      path: baseUri.path + normalizedPath,
      queryParameters: queryParameters?.map(
        (key, value) => MapEntry(key, value?.toString()),
      ),
    );
  }
}
