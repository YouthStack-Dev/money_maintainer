// ignore_for_file: prefer_interpolation_to_compose_strings, curly_braces_in_flow_control_structures
import 'package:flutter/material.dart';
import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../data/accounts_api.dart';

class AccountsPage extends StatefulWidget {
  const AccountsPage({required this.accessToken, super.key});
  final String accessToken;
  @override State<AccountsPage> createState() => _AccountsPageState();
}

class _AccountsPageState extends State<AccountsPage> {
  late final AccountsApi api;
  List<AccountItem> items = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    api = AccountsApi(config: AppEnvironmentConfig.development);
    load();
  }

  Future<void> load() async {
    if (!mounted) return;
    setState(() { loading = true; error = null; });
    try {
      final value = await api.list(widget.accessToken);
      if (mounted) setState(() => items = value.where((a) => a.active).toList());
    } catch (e) {
      if (mounted) setState(() => error = e is AppException ? e.message : 'Unable to load accounts.');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }
  Future<void> add() async {
    final r = await form();
    if (r == null) return;
    try {
      await api.create(widget.accessToken, r.name, r.type, r.institution, r.balance);
      await load();
    } catch (e) { msg(e); }
  }

  Future<void> edit(AccountItem a) async {
    final r = await form(a);
    if (r == null) return;
    try {
      await api.update(widget.accessToken, a.id, r.name, r.institution, r.balance);
      await load();
    } catch (e) { msg(e); }
  }

  Future<void> remove(AccountItem a) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Remove account?'),
        content: Text(a.name + ' will be deactivated.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Remove')),
        ],
      ),
    );
    if (ok != true) return;
    try { await api.remove(widget.accessToken, a.id); await load(); } catch (e) { msg(e); }
  }

  void msg(Object e) {
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(e is AppException ? e.message : 'Request failed.')),
    );
  }

  Future<_Form?> form([AccountItem? a]) async {
    final n = TextEditingController(text: a?.name ?? '');
    final i = TextEditingController(text: a?.institution ?? '');
    final b = TextEditingController(text: a == null ? '' : a.balance.toString());
    var type = a?.type ?? 'BANK_ACCOUNT';
    final r = await showModalBottomSheet<_Form>(
      context: context, isScrollControlled: true, showDragHandle: true,
      builder: (c) => StatefulBuilder(
        builder: (c, set) => Padding(
          padding: EdgeInsets.fromLTRB(20, 10, 20, MediaQuery.viewInsetsOf(c).bottom + 20),
          child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text(a == null ? 'Add account' : 'Edit account', style: Theme.of(c).textTheme.headlineSmall),
            TextField(controller: n, decoration: const InputDecoration(labelText: 'Account name')),
            DropdownButtonFormField<String>(
              initialValue: type, decoration: const InputDecoration(labelText: 'Account type'),
              items: const [
                DropdownMenuItem(value: 'BANK_ACCOUNT', child: Text('Bank account')),
                DropdownMenuItem(value: 'CASH', child: Text('Cash')),
                DropdownMenuItem(value: 'WALLET', child: Text('Wallet')),
                DropdownMenuItem(value: 'CREDIT_CARD', child: Text('Credit card')),
              ],
              onChanged: a == null ? (v) => set(() => type = v!) : null,
            ),
            TextField(controller: i, decoration: const InputDecoration(labelText: 'Institution')),
            TextField(controller: b, keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Opening balance', prefixText: 'INR ')),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () {
                final value = double.tryParse(b.text) ?? 0;
                if (n.text.trim().isEmpty) return;
                Navigator.pop(c, _Form(n.text.trim(), type, i.text.trim(), value));
              },
              child: Text(a == null ? 'Add account' : 'Save'),
            ),
            const SizedBox(height: 8),
          ])),
        ),
      ),
    );
    n.dispose(); i.dispose(); b.dispose();
    return r;
  }

  @override
  Widget build(BuildContext c) {
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: load,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(20, 18, 20, 100),
          children: [
            Text('Accounts', style: Theme.of(c).textTheme.headlineSmall),
            const SizedBox(height: 6),
            const Text('Bank, cash, wallet and credit accounts'),
            const SizedBox(height: 16),
            if (loading && items.isEmpty)
              const Center(child: CircularProgressIndicator())
            else if (error != null && items.isEmpty)
              Center(child: Text(error!))
            else if (items.isEmpty)
              _empty(c)
            else
              ...items.map(_tile),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: add, icon: const Icon(Icons.add), label: const Text('Add account'),
      ),
    );
  }
  Widget _empty(BuildContext c) => Card(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(children: [
        const Icon(Icons.account_balance_wallet_outlined, size: 48),
        const SizedBox(height: 10),
        Text('No accounts yet', style: Theme.of(c).textTheme.titleLarge),
        const SizedBox(height: 12),
        const Text('Add your bank account, cash or wallet to start tracking money.', textAlign: TextAlign.center),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: add, icon: const Icon(Icons.add), label: const Text('Add first account')),
      ]),
    ),
  );

  Widget _tile(AccountItem a) => Card(
    child: ListTile(
      leading: CircleAvatar(child: Icon(_icon(a.type))),
      title: Text(a.name),
      subtitle: Text(a.type.replaceAll('_', ' ') + (a.institution?.isNotEmpty == true ? ' • ' + a.institution! : '')),
      trailing: PopupMenuButton<String>(
        onSelected: (v) => v == 'edit' ? edit(a) : remove(a),
        itemBuilder: (_) => const [
          PopupMenuItem(value: 'edit', child: Text('Edit')),
          PopupMenuItem(value: 'remove', child: Text('Remove')),
        ],
      ),
    ),
  );

  IconData _icon(String t) => switch (t) {
    'BANK_ACCOUNT' => Icons.account_balance_outlined,
    'CASH' => Icons.payments_outlined,
    'CREDIT_CARD' => Icons.credit_card_outlined,
    _ => Icons.account_balance_wallet_outlined,
  };
}
class _Form {
  const _Form(this.name, this.type, this.institution, this.balance);
  final String name, type, institution;
  final double balance;
}
