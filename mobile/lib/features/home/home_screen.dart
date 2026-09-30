import 'package:flutter/material.dart';
import 'home_data.dart';
import 'home_service.dart';
import '../quick_add/quick_add_screen.dart';
import '../activity/activity_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _service = HomeService();
  late Future<HomeData> _home;

  @override void initState() { super.initState(); _home = _service.load(); }
  Future<void> _refresh() async { setState(() => _home = _service.load()); await _home; }
  String _money(double value) => '₹${value.toStringAsFixed(0)}';

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Money Maintainer'), actions: [IconButton(icon: const Icon(Icons.history), tooltip: 'Activity', onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ActivityScreen()))), IconButton(icon: const Icon(Icons.add), tooltip: 'Quick Add', onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const QuickAddScreen())))],),
    body: FutureBuilder<HomeData>(
      future: _home,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) return _ErrorState(onRetry: _refresh);
        final d = snapshot.data!;
        return RefreshIndicator(
          onRefresh: _refresh,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _HeroCard(title: 'Available money', value: _money(d.availableMoney)),
              const SizedBox(height: 16),
              _StatGrid(items: [
                ('This month spending', _money(d.spending)),
                ('Income', _money(d.income)),
                ('Net cash flow', _money(d.netCashFlow)),
                ('Budget remaining', _money(d.budgetRemaining)),
              ]),
              const SizedBox(height: 16),
              _StatGrid(items: [
                ('CC outstanding', _money(d.creditCardOutstanding)),
                ('Owed to you', _money(d.moneyOwedToUser)),
                ('You owe', _money(d.moneyUserOwes)),
                ('Office pending', _money(d.officePending)),
              ]),
              const SizedBox(height: 16),
              _Section(title: 'Planning', child: Text(
                '${d.activeGoalCount} active goals · ${d.goalsNearDeadline} near deadline · '
                '${d.upcomingDebtCount} upcoming debts · ${d.overdueDebtCount} overdue debts',
              )),
              const SizedBox(height: 12),
              _Section(title: 'Alerts', child: Text('${d.unreadAlertCount} unread alerts')),
              const SizedBox(height: 12),
              _Section(
                title: 'Top spending',
                child: d.topSpendingCategories.isEmpty
                    ? const Text('No spending recorded yet.')
                    : Column(children: d.topSpendingCategories.map((item) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text('${item['category'] ?? 'Uncategorized'}'),
                        trailing: Text(_money(double.tryParse('${item['amount'] ?? 0}') ?? 0)),
                      )).toList()),
              ),
              const SizedBox(height: 12),
              _Section(
                title: 'Recent activity',
                child: d.recentActivity.isEmpty
                    ? const Text('No recent activity.')
                    : Column(children: d.recentActivity.map((item) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text('${item['description'] ?? 'Transaction'}'),
                        subtitle: Text('${item['type'] ?? ''} · ${item['date'] ?? ''}'),
                        trailing: Text(_money(double.tryParse('${item['amount'] ?? 0}') ?? 0)),
                      )).toList()),
              ),
            ],
          ),
        );
      },
    ),
  );
}

class _HeroCard extends StatelessWidget {
  const _HeroCard({required this.title, required this.value});
  final String title, value;
  @override Widget build(BuildContext context) => Card(
    child: Padding(padding: const EdgeInsets.all(20), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [Text(title), const SizedBox(height: 8),
        Text(value, style: Theme.of(context).textTheme.headlineMedium)],
    )),
  );
}

class _StatGrid extends StatelessWidget {
  const _StatGrid({required this.items});
  final List<(String, String)> items;
  @override Widget build(BuildContext context) => GridView.builder(
    shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
    itemCount: items.length,
    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
      crossAxisCount: 2, mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: 1.65),
    itemBuilder: (_, i) => Card(child: Padding(padding: const EdgeInsets.all(14),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(items[i].$1), const Spacer(),
        Text(items[i].$2, style: Theme.of(context).textTheme.titleLarge),
      ]))),
  );
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.child});
  final String title; final Widget child;
  @override Widget build(BuildContext context) => Card(
    child: Padding(padding: const EdgeInsets.all(16), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [Text(title, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8), child],
    )),
  );
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.onRetry});
  final Future<void> Function() onRetry;
  @override Widget build(BuildContext context) => Center(child: Padding(
    padding: const EdgeInsets.all(24),
    child: Column(mainAxisSize: MainAxisSize.min, children: [
      const Text('Could not load your finances.'),
      const SizedBox(height: 12),
      FilledButton(onPressed: onRetry, child: const Text('Retry')),
    ]),
  ));
}
