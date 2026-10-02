// ignore_for_file: prefer_interpolation_to_compose_strings
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/auth/auth_token_refresher.dart';
import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';

class AccountItem {
  const AccountItem({
    required this.id,
    required this.name,
    required this.type,
    required this.institution,
    required this.balance,
    required this.active,
  });

  final int id;
  final String name;
  final String type;
  final String? institution;
  final double balance;
  final bool active;

  factory AccountItem.fromJson(Map<String, dynamic> json) => AccountItem(
    id: (json['id'] as num).toInt(),
    name: json['name']?.toString() ?? '',
    type: json['account_type']?.toString() ?? 'CASH',
    institution: json['institution_name']?.toString(),
    balance: (json['opening_balance'] as num?)?.toDouble() ?? 0,
    active: json['is_active'] == true,
  );
}

class AccountsApi {
  AccountsApi({required this.config, http.Client? client})
      : _client = client ?? http.Client();

  final AppEnvironmentConfig config;
  final http.Client _client;
  static const _timeout = Duration(seconds: 15);

  Map<String, String> _headers(String token) => {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + token,
  };

  Uri _uri(String path) {
    final base = Uri.parse(config.apiBaseUrl);
    return base.replace(path: base.path + path);
  }

  Future<http.Response> _request(
    String token,
    Future<http.Response> Function(String token) call,
  ) async {
    try {
      var response = await call(token).timeout(_timeout);
      if (response.statusCode == 401) {
        final refreshed = await AuthTokenRefresher.refresh(config);
        if (refreshed != null) {
          response = await call(refreshed).timeout(_timeout);
        }
      }
      return response;
    } on TimeoutException {
      throw const NetworkException(
        'The server took too long to respond. Please try again.',
      );
    } on AppException {
      rethrow;
    } catch (error) {
      throw NetworkException('Unable to reach the server: ' + error.toString());
    }
  }

  dynamic _decode(http.Response response) {
    dynamic data;
    try {
      data = jsonDecode(response.body);
    } catch (_) {
      throw ApiException(
        'Invalid server response.',
        statusCode: response.statusCode,
      );
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      final detail = data is Map<String, dynamic> ? data['detail'] : null;
      var message = response.statusCode == 401
          ? 'Your session expired. Please sign in again.'
          : 'Account request failed (' +
                response.statusCode.toString() +
                ').';
      if (detail is String && detail.trim().isNotEmpty) {
        message = detail;
      } else if (detail is List && detail.isNotEmpty) {
        final first = detail.first;
        if (first is Map && first['msg'] != null) {
          message = first['msg'].toString();
        }
      }
      throw ApiException(message, statusCode: response.statusCode);
    }

    return data;
  }

  Future<List<AccountItem>> list(String token) async {
    final response = await _request(
      token,
      (accessToken) =>
          _client.get(_uri('/api/v1/accounts'), headers: _headers(accessToken)),
    );
    final data = _decode(response) as List;
    final seen = <int>{};
    return data
        .map(
          (item) =>
              AccountItem.fromJson(Map<String, dynamic>.from(item as Map)),
        )
        .where((account) => seen.add(account.id))
        .toList();
  }

  Future<AccountItem> create(
    String token,
    String name,
    String type,
    String institution,
    double balance,
  ) async {
    final response = await _request(
      token,
      (accessToken) => _client.post(
        _uri('/api/v1/accounts'),
        headers: {..._headers(accessToken), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'account_type': type,
          'institution_name': institution.isEmpty ? null : institution,
          'currency': 'INR',
          'opening_balance': balance,
        }),
      ),
    );
    return AccountItem.fromJson(
      Map<String, dynamic>.from(_decode(response) as Map),
    );
  }

  Future<AccountItem> update(
    String token,
    int id,
    String name,
    String institution,
    double balance,
  ) async {
    final response = await _request(
      token,
      (accessToken) => _client.patch(
        _uri('/api/v1/accounts/' + id.toString()),
        headers: {..._headers(accessToken), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'institution_name': institution.isEmpty ? null : institution,
          'opening_balance': balance,
        }),
      ),
    );
    return AccountItem.fromJson(
      Map<String, dynamic>.from(_decode(response) as Map),
    );
  }

  Future<void> remove(String token, int id) async {
    final response = await _request(
      token,
      (accessToken) => _client.delete(
        _uri('/api/v1/accounts/' + id.toString()),
        headers: _headers(accessToken),
      ),
    );
    _decode(response);
  }
}
