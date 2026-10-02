import 'package:flutter/material.dart';

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../data/dashboard_api.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({required this.accessToken, super.key});

  final String accessToken;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  late final DashboardApi _api;
  DashboardData? _data;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _api = DashboardApi(config: AppEnvironmentConfig.development);
    if (widget.accessToken.isEmpty) {
      _loading = false;
      _error = 'No authenticated session.';
    } else {
      _load();
    }
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await _api.load(widget.accessToken);
      if (!mounted) return;
      setState(() => _data = data);
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } on NetworkException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } catch (_) {
      if (mounted) setState(() => _error = 'Unable to load your dashboard.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _data == null) {
      return const SafeArea(
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (_data == null) {
      return SafeArea(
        child: RefreshIndicator(
          onRefresh: _load,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(24),
            children: [
              const SizedBox(height: 120),
              Text(
                'Your money at a glance',
                style: Theme.of(context).textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              const Icon(Icons.cloud_off_outlined, size: 48),
              const SizedBox(height: 16),
              Text(
                _error ?? 'Unable to load dashboard.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _load,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    final data = _data!;
    return SafeArea(
      child: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
          children: [
            Text(
              'Your money at a glance',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            _BalanceCard(data: data),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _MetricCard(
                    title: 'Income',
                    value: _money(data.income),
                    icon: Icons.arrow_downward_rounded,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _MetricCard(
                    title: 'Spent',
                    value: _money(data.spending),
                    icon: Icons.arrow_upward_rounded,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _SectionCard(
              title: 'Budget',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${_money(data.budgetSpent)} of ${_money(data.budgetTotal)}',
                  ),
                  const SizedBox(height: 10),
                  LinearProgressIndicator(
                    value: data.budgetTotal <= 0
                        ? 0
                        : (data.budgetSpent / data.budgetTotal).clamp(0, 1),
                  ),
                  const SizedBox(height: 8),
                  Text('${_money(data.budgetRemaining)} remaining'),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _MetricCard(
                    title: 'Credit',
                    value: _money(data.creditOutstanding),
                    icon: Icons.credit_card_outlined,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _MetricCard(
                    title: 'Net worth',
                    value: _money(data.netWorth),
                    icon: Icons.account_balance_outlined,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _SectionCard(
              title: 'Money & office',
              child: Column(
                children: [
                  _InfoRow('You are owed', _money(data.moneyOwed)),
                  _InfoRow('You owe', _money(data.moneyOwes)),
                  _InfoRow('Office pending', _money(data.officePending)),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _SectionCard(
              title: 'Recent activity',
              child: data.recentActivity.isEmpty
                  ? const Text('No transactions this month.')
                  : Column(
                      children: data.recentActivity
                          .map(
                            (item) => ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: CircleAvatar(
                                child: Icon(_transactionIcon(item.type)),
                              ),
                              title: Text(
                                item.description.isEmpty
                                    ? 'Transaction'
                                    : item.description,
                              ),
                              subtitle: Text(
                                item.date == null
                                    ? item.type
                                    : _date(item.date!),
                              ),
                              trailing: Text(
                                '${item.type == 'EXPENSE' ? '-' : '+'}${_money(item.amount)}',
                              ),
                            ),
                          )
                          .toList(growable: false),
                    ),
            ),
            const SizedBox(height: 16),
            _SectionCard(
              title: 'Alerts',
              child: Text(
                data.unreadAlerts == 0
                    ? 'No unread alerts.'
                    : '${data.unreadAlerts} unread alert${data.unreadAlerts == 1 ? '' : 's'}.',
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _money(double value) => '₹ ${value.toStringAsFixed(2)}';

  String _date(DateTime value) =>
      '${value.day.toString().padLeft(2, '0')}/${value.month.toString().padLeft(2, '0')}/${value.year}';

  IconData _transactionIcon(String type) {
    switch (type) {
      case 'INCOME':
      case 'REFUND':
        return Icons.arrow_downward_rounded;
      case 'EXPENSE':
        return Icons.arrow_upward_rounded;
      default:
        return Icons.swap_horiz_rounded;
    }
  }
}

class _BalanceCard extends StatelessWidget {
  const _BalanceCard({required this.data});

  final DashboardData data;

  @override
  Widget build(BuildContext context) {
    final flow = data.netCashFlow >= 0 ? '+' : '';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Available money',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 8),
            Text(
              '₹ ${data.availableMoney.toStringAsFixed(2)}',
              style: Theme.of(context).textTheme.displaySmall,
            ),
            const SizedBox(height: 12),
            Text(
              'Net cash flow $flow₹ ${data.netCashFlow.toStringAsFixed(2)} this month',
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.title,
    required this.value,
    required this.icon,
  });

  final String title;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon),
            const SizedBox(height: 10),
            Text(title),
            const SizedBox(height: 4),
            Text(value, style: Theme.of(context).textTheme.titleLarge),
          ],
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow(this.label, this.value);

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(label), Text(value)],
      ),
    );
  }
}
