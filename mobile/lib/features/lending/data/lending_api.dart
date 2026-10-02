// ignore_for_file: prefer_interpolation_to_compose_strings
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/auth/auth_token_refresher.dart';
import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';

class LendingItem {
  const LendingItem({
    required this.id,
    required this.direction,
    required this.personName,
    required this.description,
    required this.originalAmount,
    required this.outstandingAmount,
    required this.dueDate,
    required this.status,
  });

  final int id;
  final String direction;
  final String personName;
  final String? description;
  final double originalAmount;
  final double outstandingAmount;
  final DateTime? dueDate;
  final String status;

  factory LendingItem.fromJson(Map<String, dynamic> json) => LendingItem(
    id: (json['id'] as num).toInt(),
    direction: json['direction']?.toString() ?? 'LENT',
    personName: json['person_name']?.toString() ?? '',
    description: json['description']?.toString(),
    originalAmount: (json['original_amount'] as num).toDouble(),
    outstandingAmount: (json['outstanding_amount'] as num).toDouble(),
    dueDate: json['due_date'] == null
        ? null
        : DateTime.parse(json['due_date'].toString()),
    status: json['status']?.toString() ?? 'ACTIVE',
  );
}

class LendingSummary {
  const LendingSummary({
    required this.borrowed,
    required this.lent,
    required this.borrowedCount,
    required this.lentCount,
  });

  final double borrowed;
  final double lent;
  final int borrowedCount;
  final int lentCount;

  factory LendingSummary.fromJson(Map<String, dynamic> json) => LendingSummary(
    borrowed: (json['total_borrowed_outstanding'] as num).toDouble(),
    lent: (json['total_lent_outstanding'] as num).toDouble(),
    borrowedCount: (json['active_borrowed_count'] as num).toInt(),
    lentCount: (json['active_lent_count'] as num).toInt(),
  );
}

class LendingAccount {
  const LendingAccount({required this.id, required this.name});

  final int id;
  final String name;

  factory LendingAccount.fromJson(Map<String, dynamic> json) => LendingAccount(
    id: (json['id'] as num).toInt(),
    name: json['name']?.toString() ?? '',
  );
}

class LendingApi {
  LendingApi({required this.config, http.Client? client})
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

  dynamic _decode(http.Response response, String fallback) {
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
          : fallback;
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

  Future<List<LendingItem>> list(String token) async {
    final response = await _request(
      token,
      (accessToken) => _client.get(_uri('/api/v1/debts'), headers: _headers(accessToken)),
    );
    final data = _decode(response, 'Unable to load lending records.') as List;
    return data
        .map(
          (item) =>
              LendingItem.fromJson(Map<String, dynamic>.from(item as Map)),
        )
        .toList();
  }

  Future<LendingSummary> summary(String token) async {
    final response = await _request(
      () =>
          _client.get(_uri('/api/v1/debts/summary'), headers: _headers(token)),
    );
    return LendingSummary.fromJson(
      Map<String, dynamic>.from(
        _decode(response, 'Unable to load lending summary.') as Map,
      ),
    );
  }

  Future<List<LendingAccount>> accounts(String token) async {
    final response = await _request(
      () => _client.get(_uri('/api/v1/accounts'), headers: _headers(token)),
    );
    final data = _decode(response, 'Unable to load accounts.') as List;
    final seen = <int>{};
    return data
        .map(
          (item) =>
              LendingAccount.fromJson(Map<String, dynamic>.from(item as Map)),
        )
        .where((account) => seen.add(account.id))
        .toList();
  }

  Future<LendingItem> create(
    String token, {
    required String direction,
    required int accountId,
    required String personName,
    required double amount,
    String? description,
    DateTime? dueDate,
  }) async {
    final response = await _request(
      () => _client.post(
        _uri('/api/v1/debts'),
        headers: {..._headers(accessToken), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'direction': direction,
          'account_id': accountId,
          'person_name': personName.trim(),
          'description': description?.trim().isEmpty == true
              ? null
              : description?.trim(),
          'original_amount': amount,
          'due_date': dueDate?.toIso8601String().substring(0, 10),
        }),
      ),
    );
    return LendingItem.fromJson(
      Map<String, dynamic>.from(
        _decode(response, 'Unable to create lending record.') as Map,
      ),
    );
  }

  Future<void> repay(
    String token, {
    required int debtId,
    required int accountId,
    required double amount,
    required DateTime date,
    String? note,
  }) async {
    final response = await _request(
      () => _client.post(
        _uri('/api/v1/debts/' + debtId.toString() + '/repayments'),
        headers: {..._headers(token), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': accountId,
          'amount': amount,
          'repayment_date': date.toIso8601String().substring(0, 10),
          'note': note?.trim().isEmpty == true ? null : note?.trim(),
        }),
      ),
    );
    _decode(response, 'Unable to record repayment.');
  }

  Future<void> cancel(String token, int id) async {
    final response = await _request(
      () => _client.delete(
        _uri('/api/v1/debts/' + id.toString()),
        headers: _headers(token),
      ),
    );
    _decode(response, 'Unable to cancel this record.');
  }
}
