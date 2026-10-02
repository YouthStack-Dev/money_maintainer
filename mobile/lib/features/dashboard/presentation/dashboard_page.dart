import 'package:flutter/material.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
        children: [
          Text('Good morning', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          Text('Your money at a glance',
              style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Total balance',
                      style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 8),
                  Text('₹ 42,850',
                      style: Theme.of(context).textTheme.displaySmall),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: _Metric(label: 'Income', value: '₹ 30,000',
                          icon: Icons.arrow_downward_rounded)),
                      Expanded(child: _Metric(label: 'Spent', value: '₹ 12,450',
                          icon: Icons.arrow_upward_rounded)),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: _QuickAction(
                label: 'Add expense',
                icon: Icons.remove_circle_outline,
                onTap: () => _showComingSoon(context, 'Expense entry'),
              )),
              const SizedBox(width: 12),
              Expanded(child: _QuickAction(
                label: 'Add income',
                icon: Icons.add_circle_outline,
                onTap: () => _showComingSoon(context, 'Income entry'),
              )),
            ],
          ),
          const SizedBox(height: 24),
          Text('This month', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: CircleAvatar(
                    backgroundColor: scheme.primaryContainer,
                    child: Icon(Icons.directions_subway_outlined,
                        color: scheme.onPrimaryContainer),
                  ),
                  title: const Text('Metro'),
                  subtitle: const Text('Personal · Today'),
                  trailing: const Text('− ₹80'),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: CircleAvatar(
                    backgroundColor: scheme.secondaryContainer,
                    child: Icon(Icons.receipt_long_outlined,
                        color: scheme.onSecondaryContainer),
                  ),
                  title: const Text('Office reimbursement'),
                  subtitle: const Text('Office · Yesterday'),
                  trailing: const Text('+ ₹1,300'),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: CircleAvatar(
                    backgroundColor: scheme.tertiaryContainer,
                    child: Icon(Icons.account_balance_wallet_outlined,
                        color: scheme.onTertiaryContainer),
                  ),
                  title: const Text('Salary'),
                  subtitle: const Text('Income · 30 Sep'),
                  trailing: const Text('+ ₹30,000'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Text('Financial snapshot',
              style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Row(
            children: const [
              Expanded(child: _SnapshotCard(
                title: 'Credit',
                value: '₹ 8,350',
                icon: Icons.credit_card_outlined,
              )),
              SizedBox(width: 12),
              Expanded(child: _SnapshotCard(
                title: 'You owe',
                value: '₹ 4,000',
                icon: Icons.handshake_outlined,
              )),
            ],
          ),
        ],
      ),
    );
  }

  void _showComingSoon(BuildContext context, String feature) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$feature will be connected to the API next.')),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value, required this.icon});
  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Icon(icon, size: 18),
      const SizedBox(width: 6),
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(value, style: Theme.of(context).textTheme.titleMedium),
      ]),
    ],
  );
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({required this.label, required this.icon, required this.onTap});
  final String label;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    onPressed: onTap,
    icon: Icon(icon),
    label: Text(label),
    style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
  );
}

class _SnapshotCard extends StatelessWidget {
  const _SnapshotCard({required this.title, required this.value, required this.icon});
  final String title;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(icon),
        const SizedBox(height: 12),
        Text(title, style: Theme.of(context).textTheme.bodyMedium),
        const SizedBox(height: 4),
        Text(value, style: Theme.of(context).textTheme.titleLarge),
      ]),
    ),
  );
}
