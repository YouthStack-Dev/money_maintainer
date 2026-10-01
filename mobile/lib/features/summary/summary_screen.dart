import 'package:flutter/material.dart';
import 'summary_service.dart';

class SummaryScreen extends StatefulWidget {
  const SummaryScreen({super.key});
  @override
  State<SummaryScreen> createState() => _SummaryScreenState();
}

class _SummaryScreenState extends State<SummaryScreen> {
  final _service = SummaryService();
  late Future<FinancialSummary> _future;
  @override
  void initState() {
    super.initState();
    _future = _service.get();
  }

  Future<void> _refresh() async {
    setState(() => _future = _service.get());
    await _future;
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(title: const Text('Financial summary')),
      body: FutureBuilder<FinancialSummary>(
          future: _future,
          builder: (c, s) {
            if (s.connectionState != ConnectionState.done)
              return const Center(child: CircularProgressIndicator());
            if (s.hasError)
              return Center(
                  child: FilledButton(
                      onPressed: _refresh, child: const Text('Retry')));
            final x = s.data!;
            return RefreshIndicator(
                onRefresh: _refresh,
                child: ListView(padding: const EdgeInsets.all(16), children: [
                  _metric('Net worth', x.netWorth),
                  _metric('Total assets', x.assets),
                  _metric('Credit card debt', x.cardDebt),
                  _metric('Income', x.income),
                  _metric('Expenses', x.expenses),
                  _metric('Refunds', x.refunds),
                  _metric('Net cash flow', x.netCashFlow),
                  const SizedBox(height: 12),
                  Text('Accounts',
                      style: Theme.of(context).textTheme.titleLarge),
                  ...x.accounts.map((a) => ListTile(
                      title: Text('${a['name'] ?? ''}'),
                      subtitle: Text('${a['account_type'] ?? ''}'),
                      trailing: Text(
                          '₹${FinancialSummary._n(a['current_balance']).toStringAsFixed(2)}')))
                ]));
          }));
  Widget _metric(String title, double value) => Card(
      child: ListTile(
          title: Text(title),
          trailing: Text('₹${value.toStringAsFixed(2)}',
              style: const TextStyle(fontWeight: FontWeight.bold))));
}
