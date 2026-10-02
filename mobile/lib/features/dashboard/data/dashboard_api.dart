import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';

class DashboardData {
  const DashboardData({
    required this.availableMoney,
    required this.spending,
    required this.income,
    required this.refunds,
    required this.netCashFlow,
    required this.budgetTotal,
    required this.budgetSpent,
    required this.budgetRemaining,
    required this.creditOutstanding,
    required this.moneyOwed,
    required this.moneyOwes,
    required this.officePending,
    required this.activeGoals,
    required this.goalsNearDeadline,
    required this.overdueDebts,
    required this.upcomingDebts,
    required this.unreadAlerts,
    required this.recentActivity,
    required this.netWorth,
    required this.totalAssets,
    required this.totalLiabilities,
  });

  final double availableMoney;
  final double spending;
  final double income;
  final double refunds;
  final double netCashFlow;
  final double budgetTotal;
  final double budgetSpent;
  final double budgetRemaining;
  final double creditOutstanding;
  final double moneyOwed;
  final double moneyOwes;
  final double officePending;
  final int activeGoals;
  final int goalsNearDeadline;
  final int overdueDebts;
  final int upcomingDebts;
  final int unreadAlerts;
  final List<RecentActivity> recentActivity;
  final double netWorth;
  final double totalAssets;
  final double totalLiabilities;
}

class RecentActivity {
  const RecentActivity({
    required this.type,
    required this.amount,
    required this.description,
    required this.date,
  });

  final String type;
  final double amount;
  final String description;
  final DateTime? date;
}

class DashboardApi {
  DashboardApi({required this.config, http.Client? client})
      : _client = client ?? http.Client();

  final AppEnvironmentConfig config;
  final http.Client _client;

  static const _timeout = Duration(seconds: 15);

  Future<DashboardData> load(String accessToken) async {
    final home = await _get('/api/v1/personal-finance-home', accessToken);
    Map<String, dynamic>? wealth;
    try {
      wealth = await _get('/api/v1/wealth-dashboard', accessToken);
    } on AppException {
      wealth = null;
    }

    return DashboardData(
      availableMoney: _number(home['available_money']),
      spending: _number(home['current_month_spending']),
      income: _number(home['current_month_income']),
      refunds: _number(home['current_month_refunds']),
      netCashFlow: _number(home['current_month_net_cash_flow']),
      budgetTotal: _number(home['budget_total']),
      budgetSpent: _number(home['budget_spent']),
      budgetRemaining: _number(home['budget_remaining']),
      creditOutstanding: _number(home['credit_card_outstanding']),
      moneyOwed: _number(home['money_owed_to_user']),
      moneyOwes: _number(home['money_user_owes']),
      officePending: _number(home['office_reimbursement_pending']),
      activeGoals: _int(home['active_goal_count']),
      goalsNearDeadline: _int(home['goals_near_deadline']),
      overdueDebts: _int(home['overdue_debt_count']),
      upcomingDebts: _int(home['upcoming_debt_count']),
      unreadAlerts: _int(home['unread_alert_count']),
      recentActivity: _recent(home['recent_activity']),
      netWorth: _number(wealth?['net_worth']),
      totalAssets: _number(wealth?['total_assets']),
      totalLiabilities: _number(wealth?['total_liabilities']),
    );
  }

  Future<Map<String, dynamic>> _get(String path, String token) async {
    try {
      final response = await _client.get(
        _uri(path),
        headers: {
          'Accept': 'application/json',
          'Authorization': 'Bearer $token',
        },
      ).timeout(_timeout);
      return _decode(response);
    } on AppException {
      rethrow;
    } on TimeoutException {
      throw const NetworkException('The server took too long to respond.');
    } catch (error) {
      throw NetworkException('Unable to reach the server: $error');
    }
  }

  Map<String, dynamic> _decode(http.Response response) {
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
      throw ApiException(
        data['detail']?.toString() ?? 'Unable to load dashboard.',
        statusCode: response.statusCode,
      );
    }
    return data;
  }

  Uri _uri(String path) {
    final base = Uri.parse(config.apiBaseUrl);
    final normalized = path.startsWith('/') ? path : '/$path';
    return base.replace(path: base.path + normalized);
  }

  static double _number(Object? value) {
    if (value is num) return value.toDouble();
    return double.tryParse(value?.toString() ?? '') ?? 0;
  }

  static int _int(Object? value) {
    if (value is num) return value.toInt();
    return int.tryParse(value?.toString() ?? '') ?? 0;
  }

  static List<RecentActivity> _recent(Object? value) {
    if (value is! List) return const [];
    return value.whereType<Map>().map((item) {
      return RecentActivity(
        type: item['type']?.toString() ?? 'TRANSACTION',
        amount: _number(item['amount']),
        description: item['description']?.toString() ?? 'Transaction',
        date: DateTime.tryParse(item['date']?.toString() ?? ''),
      );
    }).toList(growable: false);
  }
}
