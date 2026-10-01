import 'package:flutter/material.dart';
import 'finance_service.dart';
import 'add_account_screen.dart';
import 'add_category_screen.dart';
import 'account_detail_screen.dart';
import 'category_detail_screen.dart';
import 'financial_relationship_screen.dart';

class ManageFinancesScreen extends StatefulWidget {
  const ManageFinancesScreen({super.key});
  @override
  State<ManageFinancesScreen> createState() => _ManageFinancesScreenState();
}

class _ManageFinancesScreenState extends State<ManageFinancesScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs = TabController(length: 2, vsync: this);
  final _service = FinanceService();
  late Future<List<FinanceAccount>> _accounts;
  late Future<List<FinanceCategory>> _categories;
  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    _accounts = _service.accounts();
    _categories = _service.categories();
  }

  Future<void> _refresh() async {
    setState(_load);
    await Future.wait([_accounts, _categories]);
  }

  Future<void> _account() async {
    final ok = await Navigator.push(
        context, MaterialPageRoute(builder: (_) => const AddAccountScreen()));
    if (ok == true && mounted) setState(_load);
  }

  Future<void> _category(String type, List<FinanceCategory> all) async {
    final parents = all.where((c) => c.type == type).toList();
    final ok = await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (_) => AddCategoryScreen(type: type, parents: parents)));
    if (ok == true && mounted) setState(_load);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(
          title: const Text('Money setup'),
          bottom: TabBar(
              controller: _tabs,
              tabs: const [Tab(text: 'Accounts'), Tab(text: 'Categories')])),
      body: TabBarView(
          controller: _tabs, children: [_accountsView(), _categoriesView()]));
  Widget _accountsView() => FutureBuilder<List<FinanceAccount>>(
      future: _accounts,
      builder: (context, s) {
        if (s.connectionState != ConnectionState.done)
          return const Center(child: CircularProgressIndicator());
        if (s.hasError) return _retry();
        final items = s.data!;
        return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView(padding: const EdgeInsets.all(16), children: [
              if (items.isEmpty)
                const Card(
                    child: Padding(
                        padding: EdgeInsets.all(20),
                        child: Text(
                            'No accounts yet. Add your cash, bank account, card or wallet to get started.'))),
              ...items.map((a) => Card(
                  child: ListTile(
                      onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                      builder: (_) =>
                                          AccountDetailScreen(account: a)))
                              .then((changed) {
                            if (changed == true && mounted) setState(_load);
                          }),
                      leading: CircleAvatar(child: Icon(_icon(a.type))),
                      title: Text(a.name),
                      subtitle: Text(_label(a.type) +
                          (a.institution == null ? '' : ' · ${a.institution}')),
                      trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text('₹${a.balance.toStringAsFixed(2)}'),
                            const Icon(Icons.chevron_right, size: 18)
                          ])))),
              const SizedBox(height: 12),
              FilledButton.icon(
                  onPressed: _account,
                  icon: const Icon(Icons.add),
                  label: const Text('Add account')),
              const SizedBox(height: 10),
              OutlinedButton.icon(
                  onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => const FinancialRelationshipScreen())),
                  icon: const Icon(Icons.people_alt_outlined),
                  label: const Text('Record lending / borrowing'))
            ]));
      });
  Widget _categoriesView() => FutureBuilder<List<FinanceCategory>>(
      future: _categories,
      builder: (context, s) {
        if (s.connectionState != ConnectionState.done)
          return const Center(child: CircularProgressIndicator());
        if (s.hasError) return _retry();
        final all = s.data!;
        final expenses = all.where((c) => c.type == 'EXPENSE').toList(),
            income = all.where((c) => c.type == 'INCOME').toList();
        return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView(padding: const EdgeInsets.all(16), children: [
              _group('Expenses', expenses, 'EXPENSE', all),
              const SizedBox(height: 12),
              _group('Income', income, 'INCOME', all)
            ]));
      });
  Widget _group(String title, List<FinanceCategory> items, String type,
          List<FinanceCategory> all) =>
      Card(
          child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 6),
                    if (items.isEmpty)
                      const Padding(
                          padding: EdgeInsets.all(8), child: Text('None yet')),
                    ...items.map((c) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: Icon(type == 'EXPENSE'
                            ? Icons.arrow_upward
                            : Icons.arrow_downward),
                        onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => CategoryDetailScreen(
                                  category: c,
                                  allCategories: all,
                                ),
                              ),
                            ).then((changed) {
                              if (changed == true && mounted) setState(_load);
                            }),
                        title: Text(c.name),
                        subtitle: c.parentId == null
                            ? null
                            : const Text('Subcategory'),
                        trailing: const Icon(Icons.chevron_right))),
                    TextButton.icon(
                        onPressed: () => _category(type, all),
                        icon: const Icon(Icons.add),
                        label: Text('Add $title category'))
                  ])));
  Widget _retry() => Center(
      child: FilledButton(
          onPressed: () => setState(_load), child: const Text('Retry')));
  IconData _icon(String t) => t == 'CASH'
      ? Icons.payments
      : t == 'BANK_ACCOUNT'
          ? Icons.account_balance
          : t == 'CREDIT_CARD'
              ? Icons.credit_card
              : Icons.account_balance_wallet;
  String _label(String t) => t == 'CASH'
      ? 'Cash'
      : t == 'BANK_ACCOUNT'
          ? 'Bank account'
          : t == 'CREDIT_CARD'
              ? 'Credit card'
              : 'Wallet';
}
