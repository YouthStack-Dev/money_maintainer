import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_environment.dart';
import '../storage/secure_storage.dart';

class AuthTokenRefresher {
  AuthTokenRefresher._();

  static final SecureStorage _storage = SecureStorage();
  static Future<String?>? _inFlight;
  static const _timeout = Duration(seconds: 15);

  static Future<String?> refresh(AppEnvironmentConfig config) {
    final existing = _inFlight;
    if (existing != null) return existing;
    final future = _refresh(config);
    _inFlight = future;
    future.whenComplete(() => _inFlight = null);
    return future;
  }

  static Future<String?> _refresh(AppEnvironmentConfig config) async {
    final refreshToken = await _storage.read('auth.refresh_token');
    if (refreshToken == null || refreshToken.isEmpty) return null;

    final base = Uri.parse(config.apiBaseUrl);
    final uri = base.replace(
      path: '${base.path}/api/v1/auth/refresh',
      queryParameters: {'refresh_token_value': refreshToken},
    );

    try {
      final response = await http
          .post(uri, headers: {'Accept': 'application/json'})
          .timeout(_timeout);

      if (response.statusCode < 200 || response.statusCode >= 300) return null;

      final data = Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      final access = data['access_token']?.toString();
      final nextRefresh = data['refresh_token']?.toString();
      if (access == null || access.isEmpty) return null;

      await _storage.write('auth.access_token', access);
      if (nextRefresh != null && nextRefresh.isNotEmpty) {
        await _storage.write('auth.refresh_token', nextRefresh);
      }
      final role = data['role']?.toString();
      if (role != null && role.isNotEmpty) {
        await _storage.write('auth.role', role);
      }
      return access;
    } catch (_) {
      return null;
    }
  }
}
