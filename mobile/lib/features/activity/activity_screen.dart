import 'package:flutter/material.dart';
import 'activity_data.dart';
import 'activity_service.dart';

class ActivityScreen extends StatefulWidget {
  const ActivityScreen({super.key});
  @override State<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityScreenState extends State<ActivityScreen> {
  final _service = ActivityService();
  String? _filter;
  late Future<List<ActivityTransaction>> _future;

  @override void initState() { super.initState(); _load(); }
  void _load() => _future = _service.load(type: _filter);
  Future<void> _refresh() async { setState(_load); await _future; }

  String _money(double value) => '₹${value.toStringAsFixed(0)}';
  String _date(DateTime value) => '${value.day.toString().padLeft(2, '0')}/${value.month.toString().padLeft(2, '0')}/${value.year}';

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Activity')),
    body: Column(children: [
      SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(children: [
          _chip('All', null), _chip('Expense', 'EXPENSE'), _chip('Income', 'INCOME'),
          _chip('Refund', 'REFUND'), _chip('Transfer', 'TRANSFER'),
        ]),
      ),
      Expanded(child: FutureBuilder<List<ActivityTransaction>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
          if (snapshot.hasError) return Center(child: FilledButton(onPressed: _refresh, child: const Text('Retry')));
          final items = snapshot.data ?? [];
          if (items.isEmpty) return const Center(child: Text('No transactions yet.'));
          return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView.separated(
              padding: const EdgeInsets.all(12), itemCount: items.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (_, i) {
                final tx = items[i];
                return ListTile(
                  leading: CircleAvatar(child: Icon(_icon(tx.type))),
                  title: Text(tx.description?.isNotEmpty == true ? tx.description! : tx.type),
                  subtitle: Text('${tx.type} · ${_date(tx.date)} · #${tx.id}'),
                  trailing: Text(_money(tx.amount)),
                );
              },
            ),
          );
        },
      )),
    ]),
  );

  Widget _chip(String label, String? value) => Padding(
    padding: const EdgeInsets.only(right: 8),
    child: ChoiceChip(label: Text(label), selected: _filter == value, onSelected: (_) {
      setState(() { _filter = value; _load(); });
    }),
  );

  IconData _icon(String type) => switch (type) {
    'INCOME' => Icons.arrow_downward,
    'REFUND' => Icons.replay,
    'TRANSFER' => Icons.swap_horiz,
    _ => Icons.arrow_upward,
  };
}
