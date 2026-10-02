import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';

class AuthSession {
  const AuthSession({
    required this.accessToken,
    required this.refreshToken,
    required this.role,
  });

  final String accessToken;
  final String refreshToken;
  final String role;
}

class CurrentUser {
  const CurrentUser({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    required this.isEmailVerified,
  });

  final int id;
  final String email;
  final String fullName;
  final String role;
  final bool isEmailVerified;
}

class AuthApi {
  AuthApi({required this.config, http.Client? client})
      : _client = client ?? http.Client();

  final AppEnvironmentConfig config;
  final http.Client _client;

  static const _timeout = Duration(seconds: 15);

  Future<AuthSession> login({
    required String email,
    required String pin,
  }) =>
      _tokenRequest('/api/v1/auth/login', {
        'email': email.trim().toLowerCase(),
        'password': pin,
      });

  Future<AuthSession> register({
    required String email,
    required String fullName,
    required String pin,
  }) =>
      _tokenRequest('/api/v1/auth/register', {
        'email': email.trim().toLowerCase(),
        'full_name': fullName.trim(),
        'password': pin,
      });

  Future<AuthSession> refresh(String refreshToken) => _tokenRequest(
        '/api/v1/auth/refresh',
        {'refresh_token_value': refreshToken},
      );

  Future<void> logout(String refreshToken) async {
    try {
      final response = await _client.post(
        _uri('/api/v1/auth/logout', {'refresh_token_value': refreshToken}),
        headers: {'Accept': 'application/json'},
      ).timeout(_timeout);
      _decodeMap(response);
    } on AppException {
      rethrow;
    } on TimeoutException {
      throw const NetworkException('The server took too long to respond.');
    } catch (error) {
      throw NetworkException('Unable to reach the server: $error');
    }
  }

  Future<CurrentUser> me(String accessToken) async {
    try {
      final response = await _client.get(
        _uri('/api/v1/auth/me'),
        headers: _headers(accessToken),
      ).timeout(_timeout);
      final data = _decodeMap(response);
      return CurrentUser(
        id: (data['id'] as num).toInt(),
        email: data['email']?.toString() ?? '',
        fullName: data['full_name']?.toString() ?? '',
        role: data['role']?.toString() ?? 'USER',
        isEmailVerified: data['is_email_verified'] == true,
      );
    } on AppException {
      rethrow;
    } on TimeoutException {
      throw const NetworkException('The server took too long to respond.');
    } catch (error) {
      throw NetworkException('Unable to reach the server: $error');
    }
  }

  Future<void> changePassword({
    required String accessToken,
    required String pin,
  }) async {
    try {
      final response = await _client.post(
        _uri('/api/v1/auth/change-password', {'password': pin}),
        headers: _headers(accessToken),
      ).timeout(_timeout);
      _decodeMap(response);
    } on AppException {
      rethrow;
    } on TimeoutException {
      throw const NetworkException('The server took too long to respond.');
    } catch (error) {
      throw NetworkException('Unable to reach the server: $error');
    }
  }

  Map<String, String> _headers(String token) => {
        'Accept': 'application/json',
        'Authorization': 'Bearer $token',
      };

  Uri _uri(String path, [Map<String, String>? query]) {
    final base = Uri.parse(config.apiBaseUrl);
    final normalized = path.startsWith('/') ? path : '/$path';
    return base.replace(
      path: base.path + normalized,
      queryParameters: query,
    );
  }

  Future<AuthSession> _tokenRequest(
    String path,
    Map<String, String> parameters,
  ) async {
    try {
      final response = await _client.post(
        _uri(path, parameters),
        headers: {'Accept': 'application/json'},
      ).timeout(_timeout);
      final data = _decodeMap(response);
      return AuthSession(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
        role: data['role']?.toString() ?? 'USER',
      );
    } on AppException {
      rethrow;
    } on TimeoutException {
      throw const NetworkException('The server took too long to respond.');
    } catch (error) {
      throw NetworkException('Unable to reach the server: $error');
    }
  }

  Map<String, dynamic> _decodeMap(http.Response response) {
    var data = <String, dynamic>{};
    if (response.body.isNotEmpty) {
      try {
        data = Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      } catch (_) {
        throw ApiException(
          'The server returned an invalid response.',
          statusCode: response.statusCode,
        );
      }
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw _apiError(response, data);
    }
    return data;
  }

  ApiException _apiError(
    http.Response response, [
    Map<String, dynamic>? decoded,
  ]) {
    return ApiException(
      (decoded ?? {})['detail']?.toString() ?? 'Request failed.',
      statusCode: response.statusCode,
    );
  }
}
