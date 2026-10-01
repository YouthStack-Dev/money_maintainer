import 'package:flutter/material.dart';
import 'finance_service.dart';
import 'edit_account_screen.dart';

class AccountDetailScreen extends StatefulWidget {
  const AccountDetailScreen({super.key, required this.account});
  final FinanceAccount account;
  @override
  State<AccountDetailScreen> createState() => _AccountDetailScreenState();
}

class _AccountDetailScreenState extends State<AccountDetailScreen> {
  final _service = FinanceService();
  late Future<FinanceAccount> _future;
  @override
  void initState() {
    super.initState();
    _future = _service.getAccount(widget.account.id);
  }

  Future<void> _delete(FinanceAccount a) async {
    final ok = await showDialog<bool>(
        context: context,
        builder: (c) => AlertDialog(
                title: const Text('Delete account?'),
                content: Text(
                    '“${a.name}” will be deactivated. Its history is kept safe.'),
                actions: [
                  TextButton(
                      onPressed: () => Navigator.pop(c, false),
                      child: const Text('Cancel')),
                  FilledButton(
                      onPressed: () => Navigator.pop(c, true),
                      child: const Text('Delete'))
                ]));
    if (ok != true) return;
    try {
      await _service.deleteAccount(a.id);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted)
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Account details')),
      body: FutureBuilder<FinanceAccount>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || snapshot.data == null) {
            return const Center(child: Text('Unable to load this account.'));
          }
          final a = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(a.name,
                          style: Theme.of(context).textTheme.headlineSmall),
                      const SizedBox(height: 8),
                      Text(_type(a.type)),
                      if (a.institution != null) Text(a.institution!),
                      const SizedBox(height: 20),
                      Text('Opening balance',
                          style: Theme.of(context).textTheme.labelLarge),
                      Text('₹${a.balance.toStringAsFixed(2)}',
                          style: Theme.of(context).textTheme.headlineMedium),
                      const SizedBox(height: 8),
                      Text('Account ID: ${a.id}'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (_) => EditAccountScreen(account: a)))
                    .then((ok) {
                  if (ok == true && mounted)
                    setState(() => _future = _service.getAccount(a.id));
                }),
                icon: const Icon(Icons.edit),
                label: const Text('Edit account'),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                  onPressed: () => _delete(a),
                  icon: const Icon(Icons.delete_outline),
                  label: const Text('Delete account')),
            ],
          );
        },
      ),
    );
  }

  String _type(String t) => t == 'BANK_ACCOUNT'
      ? 'Bank account'
      : t == 'CREDIT_CARD'
          ? 'Credit card'
          : t == 'WALLET'
              ? 'Wallet'
              : 'Cash';
}
