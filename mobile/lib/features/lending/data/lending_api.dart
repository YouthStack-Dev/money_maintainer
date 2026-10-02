// ignore_for_file: prefer_interpolation_to_compose_strings, curly_braces_in_flow_control_structures
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
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
  final String direction, personName;
  final String? description;
  final double originalAmount, outstandingAmount;
  final DateTime? dueDate;
  final String status;
  factory LendingItem.fromJson(Map<String, dynamic> j) => LendingItem(
    id: (j['id'] as num).toInt(),
    direction: j['direction']?.toString() ?? 'LENT',
    personName: j['person_name']?.toString() ?? '',
    description: j['description']?.toString(),
    originalAmount: (j['original_amount'] as num).toDouble(),
    outstandingAmount: (j['outstanding_amount'] as num).toDouble(),
    dueDate: j['due_date'] == null
        ? null
        : DateTime.parse(j['due_date'].toString()),
    status: j['status']?.toString() ?? 'ACTIVE',
  );
}

class LendingSummary {
  const LendingSummary({
    required this.borrowed,
    required this.lent,
    required this.borrowedCount,
    required this.lentCount,
  });
  final double borrowed, lent;
  final int borrowedCount, lentCount;
  factory LendingSummary.fromJson(Map<String, dynamic> j) => LendingSummary(
    borrowed: (j['total_borrowed_outstanding'] as num).toDouble(),
    lent: (j['total_lent_outstanding'] as num).toDouble(),
    borrowedCount: (j['active_borrowed_count'] as num).toInt(),
    lentCount: (j['active_lent_count'] as num).toInt(),
  );
}

class LendingAccount {
  const LendingAccount({required this.id, required this.name});
  final int id;
  final String name;
  factory LendingAccount.fromJson(Map<String, dynamic> j) => LendingAccount(
    id: (j['id'] as num).toInt(),
    name: j['name']?.toString() ?? '',
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
    final b = Uri.parse(config.apiBaseUrl);
    return b.replace(path: b.path + path);
  }

  Future<http.Response> _request(Future<http.Response> Function() call) async {
    try {
      return await call().timeout(_timeout);
    } on TimeoutException {
      throw const NetworkException('The server took too long to respond.');
    } catch (e) {
      if (e is AppException) rethrow;
      throw NetworkException('Unable to reach the server: ' + e.toString());
    }
  }

  dynamic _decode(http.Response r, String fallback) {
    dynamic d;
    try {
      d = jsonDecode(r.body);
    } catch (_) {
      throw ApiException('Invalid server response.', statusCode: r.statusCode);
    }
    if (r.statusCode < 200 || r.statusCode >= 300)
      throw ApiException(
        d is Map ? d['detail']?.toString() ?? fallback : fallback,
        statusCode: r.statusCode,
      );
    return d;
  }

  Future<List<LendingItem>> list(String token) async {
    final r = await _request(
      () => _client.get(_uri('/api/v1/debts'), headers: _headers(token)),
    );
    final d = _decode(r, 'Unable to load lending records.') as List;
    return d
        .map((x) => LendingItem.fromJson(Map<String, dynamic>.from(x as Map)))
        .toList();
  }

  Future<LendingSummary> summary(String token) async {
    final r = await _request(
      () =>
          _client.get(_uri('/api/v1/debts/summary'), headers: _headers(token)),
    );
    return LendingSummary.fromJson(
      Map<String, dynamic>.from(
        _decode(r, 'Unable to load lending summary.') as Map,
      ),
    );
  }

  Future<List<LendingAccount>> accounts(String token) async {
    final r = await _request(
      () => _client.get(_uri('/api/v1/accounts'), headers: _headers(token)),
    );
    final d = _decode(r, 'Unable to load accounts.') as List;
    return d
        .map(
          (x) => LendingAccount.fromJson(Map<String, dynamic>.from(x as Map)),
        )
        .toList();
  }

  Future<void> create(
    String token, {
    required String direction,
    required int accountId,
    required String personName,
    required double amount,
    String? description,
    DateTime? dueDate,
  }) async {
    final r = await _request(
      () => _client.post(
        _uri('/api/v1/debts'),
        headers: {..._headers(token), 'Content-Type': 'application/json'},
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
    _decode(r, 'Unable to create lending record.');
  }

  Future<void> repay(
    String token, {
    required int debtId,
    required int accountId,
    required double amount,
    required DateTime date,
    String? note,
  }) async {
    final r = await _request(
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
    _decode(r, 'Unable to record repayment.');
  }

  Future<void> cancel(String token, int id) async {
    final r = await _request(
      () => _client.delete(
        _uri('/api/v1/debts/' + id.toString()),
        headers: _headers(token),
      ),
    );
    _decode(r, 'Unable to cancel this record.');
  }
}
