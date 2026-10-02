// ignore_for_file: prefer_interpolation_to_compose_strings
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/auth/auth_token_refresher.dart';
import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';

class CreditCardSummary {
  const CreditCardSummary({
    required this.accountId,
    required this.name,
    required this.institution,
    required this.limit,
    required this.balance,
    required this.outstanding,
    required this.available,
    required this.overLimit,
    required this.utilization,
    required this.statementDay,
    required this.dueDay,
    required this.nextDue,
  });

  final int accountId;
  final String name;
  final String? institution;
  final double limit;
  final double balance;
  final double outstanding;
  final double available;
  final double overLimit;
  final double utilization;
  final int statementDay;
  final int dueDay;
  final DateTime nextDue;

  factory CreditCardSummary.fromJson(Map<String, dynamic> json) =>
      CreditCardSummary(
        accountId: (json['account_id'] as num).toInt(),
        name: json['name']?.toString() ?? '',
        institution: json['institution_name']?.toString(),
        limit: (json['credit_limit'] as num).toDouble(),
        balance: (json['current_balance'] as num).toDouble(),
        outstanding: (json['outstanding_balance'] as num).toDouble(),
        available: (json['available_credit'] as num).toDouble(),
        overLimit: (json['over_limit_amount'] as num).toDouble(),
        utilization: (json['utilization_percent'] as num).toDouble(),
        statementDay: (json['statement_day'] as num).toInt(),
        dueDay: (json['payment_due_day'] as num).toInt(),
        nextDue: DateTime.parse(json['next_payment_due_date'].toString()),
      );
}

class CreditApi {
  CreditApi({required this.config, http.Client? client})
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
        'The server took too long to respond.',
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
      final message = response.statusCode == 401
          ? 'Your session expired. Please sign in again.'
          : detail?.toString() ?? 'Credit request failed.';
      throw ApiException(message, statusCode: response.statusCode);
    }
    return data;
  }

  Future<List<CreditCardSummary>> list(String token) async {
    final response = await _request(
      token,
      (accessToken) => _client.get(
        _uri('/api/v1/credit-cards'),
        headers: _headers(accessToken),
      ),
    );
    return (_decode(response) as List)
        .map(
          (item) => CreditCardSummary.fromJson(
            Map<String, dynamic>.from(item as Map),
          ),
        )
        .toList();
  }

  Future<CreditCardSummary> configure(
    String token,
    int id, {
    required double limit,
    required int statementDay,
    required int dueDay,
  }) async {
    final response = await _request(
      token,
      (accessToken) => _client.put(
        _uri('/api/v1/credit-cards/' + id.toString()),
        headers: {..._headers(accessToken), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'credit_limit': limit,
          'statement_day': statementDay,
          'payment_due_day': dueDay,
        }),
      ),
    );
    return CreditCardSummary.fromJson(
      Map<String, dynamic>.from(_decode(response) as Map),
    );
  }
}
