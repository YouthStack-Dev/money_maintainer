import 'dart:convert';
import 'package:http/http.dart' as http;
import '../auth/token_storage.dart';
import '../config/app_config.dart';

class ApiClient {
  ApiClient({http.Client? client, TokenStorage? tokenStorage})
      : _client = client ?? http.Client(),
        _tokenStorage = tokenStorage ?? TokenStorage();

  final http.Client _client;
  final TokenStorage _tokenStorage;

  Future<dynamic> get(String path, {Map<String, String>? query}) async {
    final uri = Uri.parse('${AppConfig.apiBaseUrl}$path').replace(queryParameters: query);
    final response = await _client.get(uri, headers: await _headers());
    return _decode(response);
  }

  Future<dynamic> post(String path, {Map<String, String>? query, Object? body}) async {
    final uri = Uri.parse('${AppConfig.apiBaseUrl}$path').replace(queryParameters: query);
    final response = await _client.post(uri, headers: await _headers(), body: body == null ? null : jsonEncode(body));
    return _decode(response);
  }

  Future<Map<String, String>> _headers() async {
    final token = await _tokenStorage.accessToken();
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
    };
  }

  dynamic _decode(http.Response response) {
    dynamic body;
    try { body = response.body.isEmpty ? null : jsonDecode(response.body); }
    catch (_) { body = response.body; }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, body);
    }
    return body;
  }
}

class ApiException implements Exception {
  const ApiException(this.statusCode, this.body);
  final int statusCode;
  final dynamic body;
  @override String toString() => 'ApiException($statusCode): $body';
}
