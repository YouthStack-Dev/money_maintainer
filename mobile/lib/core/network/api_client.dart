import 'dart:async';
import 'dart:convert';
import 'dart:io';

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
    final uri = Uri.parse(AppConfig.apiBaseUrl + path)
        .replace(queryParameters: query);
    try {
      final response = await _client
          .get(uri, headers: await _headers())
          .timeout(const Duration(seconds: 20));
      return _decode(response);
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw const ApiNetworkException('The request timed out. Check your connection and try again.');
    } on SocketException {
      throw const ApiNetworkException('Unable to reach the server. Check your connection and try again.');
    } on http.ClientException {
      throw const ApiNetworkException('Unable to connect to the server. Please try again.');
    }
  }

  Future<dynamic> post(
    String path, {
    Map<String, String>? query,
    Object? body,
  }) async {
    final uri = Uri.parse(AppConfig.apiBaseUrl + path)
        .replace(queryParameters: query);
    try {
      final response = await _client
          .post(
            uri,
            headers: await _headers(),
            body: body == null ? null : jsonEncode(body),
          )
          .timeout(const Duration(seconds: 20));
      return _decode(response);
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw const ApiNetworkException('The request timed out. Check your connection and try again.');
    } on SocketException {
      throw const ApiNetworkException('Unable to reach the server. Check your connection and try again.');
    } on http.ClientException {
      throw const ApiNetworkException('Unable to connect to the server. Please try again.');
    }
  }

  Future<Map<String, String>> _headers() async {
    final token = await _tokenStorage.accessToken();
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      if (token != null && token.isNotEmpty)
        'Authorization': 'Bearer ' + token,
    };
  }

  dynamic _decode(http.Response response) {
    dynamic body;
    try {
      body = response.body.isEmpty ? null : jsonDecode(response.body);
    } catch (_) {
      body = response.body;
    }
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

  String get userMessage {
    switch (statusCode) {
      case 400:
        return _detail ?? 'The request could not be completed.';
      case 401:
        return _detail ?? 'Authentication failed. Please sign in again.';
      case 403:
        return _detail ?? 'You are not allowed to perform this action.';
      case 404:
        return 'The requested service or resource was not found.';
      case 409:
        return _detail ?? 'This information already exists.';
      case 422:
        return _detail ?? 'Please check the information you entered.';
      case 429:
        return _detail ?? 'Too many attempts. Please wait and try again later.';
      case 500:
      case 502:
      case 503:
      case 504:
        return 'The server is temporarily unavailable. Please try again later.';
      default:
        return _detail ?? 'Something went wrong. Please try again.';
    }
  }

  String? get _detail {
    if (body is String && (body as String).trim().isNotEmpty) {
      return body as String;
    }
    if (body is Map) {
      final detail = body['detail'];
      if (detail is String && detail.trim().isNotEmpty) return detail;
      if (detail is List) return _firstValidationMessage(detail);
    }
    return null;
  }

  String? _firstValidationMessage(List details) {
    for (final item in details) {
      if (item is Map) {
        final message = item['msg'];
        if (message is String && message.trim().isNotEmpty) return message;
      }
      if (item is String && item.trim().isNotEmpty) return item;
    }
    return null;
  }

  @override
  String toString() => 'ApiException(' + statusCode.toString() + '): ' + body.toString();
}

class ApiNetworkException implements Exception {
  const ApiNetworkException(this.message);

  final String message;

  @override
  String toString() => message;
}
