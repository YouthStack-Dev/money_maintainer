// ignore_for_file: prefer_interpolation_to_compose_strings
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';

class MoneyAccount {
  const MoneyAccount({
    required this.id,
    required this.name,
    required this.type,
  });

  final int id;
  final String name;
  final String type;

  factory MoneyAccount.fromJson(Map<String, dynamic> json) => MoneyAccount(
    id: (json['id'] as num).toInt(),
    name: json['name']?.toString() ?? '',
    type: json['account_type']?.toString() ?? 'CASH',
  );
}

class MoneyCategory {
  const MoneyCategory({
    required this.id,
    required this.name,
    required this.type,
  });

  final int id;
  final String name;
  final String type;

  factory MoneyCategory.fromJson(Map<String, dynamic> json) => MoneyCategory(
    id: (json['id'] as num).toInt(),
    name: json['name']?.toString() ?? '',
    type: json['category_type']?.toString() ?? 'EXPENSE',
  );
}

class MoneyTransaction {
  const MoneyTransaction({
    required this.id,
    required this.accountId,
    required this.categoryId,
    required this.transferAccountId,
    required this.type,
    required this.amount,
    required this.description,
    required this.date,
  });

  final int id;
  final int accountId;
  final int? categoryId;
  final int? transferAccountId;
  final String type;
  final String description;
  final double amount;
  final DateTime date;

  factory MoneyTransaction.fromJson(Map<String, dynamic> json) =>
      MoneyTransaction(
        id: (json['id'] as num).toInt(),
        accountId: (json['account_id'] as num).toInt(),
        categoryId: (json['category_id'] as num?)?.toInt(),
        transferAccountId: (json['transfer_account_id'] as num?)?.toInt(),
        type: json['transaction_type']?.toString() ?? 'EXPENSE',
        amount: (json['amount'] as num).toDouble(),
        description: json['description']?.toString() ?? '',
        date: DateTime.parse(json['transaction_date'].toString()).toLocal(),
      );
}

class MoneyApi {
  MoneyApi({required this.config, http.Client? client})
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

  Future<http.Response> _request(Future<http.Response> Function() call) async {
    try {
      return await call().timeout(_timeout);
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
      var message =
          'Money request failed (' + response.statusCode.toString() + ').';
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

  Future<List<MoneyAccount>> accounts(String token) async {
    final response = await _request(
      () => _client.get(_uri('/api/v1/accounts'), headers: _headers(token)),
    );
    final data = _decode(response) as List;
    final seen = <int>{};
    return data
        .map(
          (item) =>
              MoneyAccount.fromJson(Map<String, dynamic>.from(item as Map)),
        )
        .where((account) => seen.add(account.id))
        .toList();
  }

  Future<List<MoneyCategory>> categories(String token) async {
    final response = await _request(
      () => _client.get(_uri('/api/v1/categories'), headers: _headers(token)),
    );
    final data = _decode(response) as List;
    final seen = <int>{};
    return data
        .map(
          (item) =>
              MoneyCategory.fromJson(Map<String, dynamic>.from(item as Map)),
        )
        .where((category) => seen.add(category.id))
        .toList();
  }

  Future<List<MoneyTransaction>> list(String token) async {
    final response = await _request(
      () => _client.get(_uri('/api/v1/transactions'), headers: _headers(token)),
    );
    final data = _decode(response) as List;
    return data
        .map(
          (item) =>
              MoneyTransaction.fromJson(Map<String, dynamic>.from(item as Map)),
        )
        .toList();
  }

  Future<MoneyTransaction> create(
    String token, {
    required int accountId,
    int? categoryId,
    int? transferAccountId,
    required String type,
    required double amount,
    String? description,
    required DateTime date,
  }) async {
    final response = await _request(
      () => _client.post(
        _uri('/api/v1/transactions'),
        headers: {..._headers(token), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': accountId,
          'category_id': categoryId,
          'transfer_account_id': transferAccountId,
          'transaction_type': type,
          'amount': amount,
          'description': description,
          'transaction_date': date.toUtc().toIso8601String(),
        }),
      ),
    );
    return MoneyTransaction.fromJson(
      Map<String, dynamic>.from(_decode(response) as Map),
    );
  }

  Future<MoneyTransaction> update(
    String token,
    int id, {
    required int accountId,
    int? categoryId,
    int? transferAccountId,
    required String type,
    required double amount,
    String? description,
    required DateTime date,
  }) async {
    final response = await _request(
      () => _client.patch(
        _uri('/api/v1/transactions/' + id.toString()),
        headers: {..._headers(token), 'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': accountId,
          'category_id': categoryId,
          'transfer_account_id': transferAccountId,
          'transaction_type': type,
          'amount': amount,
          'description': description,
          'transaction_date': date.toUtc().toIso8601String(),
        }),
      ),
    );
    return MoneyTransaction.fromJson(
      Map<String, dynamic>.from(_decode(response) as Map),
    );
  }

  Future<void> remove(String token, int id) async {
    final response = await _request(
      () => _client.delete(
        _uri('/api/v1/transactions/' + id.toString()),
        headers: _headers(token),
      ),
    );
    _decode(response);
  }
}
