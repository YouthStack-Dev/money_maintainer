import '../../core/network/api_client.dart';

class Budget {
  Budget.fromJson(Map<String, dynamic> j)
      : id = (j['id'] as num).toInt(),
        categoryId = (j['category_id'] as num).toInt(),
        name = '${j['name'] ?? ''}',
        amount = double.tryParse('${j['amount'] ?? 0}') ?? 0,
        start = DateTime.parse('${j['period_start']}'),
        end = DateTime.parse('${j['period_end']}'),
        active = j['is_active'] != false;
  final int id, categoryId;
  final String name;
  final double amount;
  final DateTime start, end;
  final bool active;
}

class BudgetProgress {
  BudgetProgress.fromJson(Map<String, dynamic> j)
      : budgetAmount = _n(j['budget_amount']),
        spent = _n(j['spent']),
        remaining = _n(j['remaining']),
        percentage = _n(j['percentage_used']),
        overBudget = j['over_budget'] == true;
  static double _n(dynamic v) => double.tryParse('$v') ?? 0;
  final double budgetAmount, spent, remaining, percentage;
  final bool overBudget;
}

class BudgetService {
  BudgetService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;
  Future<List<Budget>> list() async {
    final d = await _api.get('/api/v1/budgets');
    return (d as List)
        .map((e) => Budget.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<Budget> get(int id) async {
    final d = await _api.get('/api/v1/budgets/$id');
    return Budget.fromJson(Map<String, dynamic>.from(d as Map));
  }

  Future<Budget> create(
      {required int categoryId,
      required String name,
      required double amount,
      required DateTime start,
      required DateTime end}) async {
    final d = await _api.post('/api/v1/budgets', body: {
      'category_id': categoryId,
      'name': name.trim(),
      'amount': amount,
      'period_start': start.toUtc().toIso8601String(),
      'period_end': end.toUtc().toIso8601String()
    });
    return Budget.fromJson(Map<String, dynamic>.from(d as Map));
  }

  Future<Budget> update(int id,
      {int? categoryId,
      String? name,
      double? amount,
      DateTime? start,
      DateTime? end,
      bool? active}) async {
    final b = <String, dynamic>{
      if (categoryId != null) 'category_id': categoryId,
      if (name != null) 'name': name.trim(),
      if (amount != null) 'amount': amount,
      if (start != null) 'period_start': start.toUtc().toIso8601String(),
      if (end != null) 'period_end': end.toUtc().toIso8601String(),
      if (active != null) 'is_active': active
    };
    final d = await _api.patch('/api/v1/budgets/$id', body: b);
    return Budget.fromJson(Map<String, dynamic>.from(d as Map));
  }

  Future<void> delete(int id) async {
    await _api.delete('/api/v1/budgets/$id');
  }

  Future<BudgetProgress> progress(int id) async {
    final d = await _api.get('/api/v1/budgets/$id/progress');
    return BudgetProgress.fromJson(Map<String, dynamic>.from(d as Map));
  }
}
