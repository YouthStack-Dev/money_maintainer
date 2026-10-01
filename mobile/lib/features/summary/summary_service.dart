import '../../core/network/api_client.dart';

class FinancialSummary {
  FinancialSummary.fromJson(Map<String, dynamic> j)
      : income = _n(j['income']),
        expenses = _n(j['expenses']),
        refunds = _n(j['refunds']),
        netCashFlow = _n(j['net_cash_flow']),
        assets = _n(j['total_assets']),
        cardDebt = _n(j['credit_card_debt']),
        netWorth = _n(j['net_worth']),
        accounts = (j['accounts'] as List? ?? [])
            .map((e) => Map<String, dynamic>.from(e as Map))
            .toList();
  static double _n(dynamic v) => double.tryParse('$v') ?? 0;
  final double income,
      expenses,
      refunds,
      netCashFlow,
      assets,
      cardDebt,
      netWorth;
  final List<Map<String, dynamic>> accounts;
}

class SummaryService {
  SummaryService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;
  Future<FinancialSummary> get() async {
    final d = await _api.get('/api/v1/summary');
    return FinancialSummary.fromJson(Map<String, dynamic>.from(d as Map));
  }
}
