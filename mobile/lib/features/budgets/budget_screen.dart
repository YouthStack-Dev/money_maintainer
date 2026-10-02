import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import '../settings/finance_service.dart';
import 'budget_service.dart';

class BudgetScreen extends StatefulWidget {
  const BudgetScreen({super.key});
  @override
  State<BudgetScreen> createState() => _BudgetScreenState();
}

class _BudgetScreenState extends State<BudgetScreen> {
  final _service = BudgetService();
  final _finance = FinanceService();
  late Future<List<Budget>> _future;
  late Future<List<FinanceCategory>> _categories;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    _future = _service.list();
    _categories = _finance.categories();
  }

  Future<void> _refresh() async {
    setState(_load);
    await Future.wait([_future, _categories]);
  }

  Future<void> _edit({Budget? budget}) async {
    final cats = await _categories;
    final expense =
        cats.where((x) => x.type == 'EXPENSE' && x.isActive).toList();
    if (!mounted) return;
    final name = TextEditingController(text: budget?.name ?? '');
    final amount =
        TextEditingController(text: budget?.amount.toStringAsFixed(2) ?? '');
    int? category = budget?.categoryId;
    DateTime start = budget?.start ?? DateTime.now();
    DateTime end = budget?.end ??
        DateTime(DateTime.now().year, DateTime.now().month + 1, 0, 23, 59);
    final ok = await showDialog<bool>(
        context: context,
        builder: (ctx) => StatefulBuilder(
            builder: (ctx, setState) => AlertDialog(
                  title: Text(budget == null ? 'Add budget' : 'Edit budget'),
                  content: SingleChildScrollView(
                      child: Column(children: [
                    TextField(
                        controller: name,
                        decoration:
                            const InputDecoration(labelText: 'Budget name')),
                    TextField(
                        controller: amount,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(labelText: 'Amount')),
                    DropdownButtonFormField<int>(
                        value: category,
                        items: expense
                            .map((x) => DropdownMenuItem(
                                value: x.id, child: Text(x.name)))
                            .toList(),
                        onChanged: (v) => setState(() => category = v),
                        decoration: const InputDecoration(
                            labelText: 'Expense category')),
                    ListTile(
                        title: Text(
                            'Start: ${start.toLocal().toString().split(' ').first}'),
                        onTap: () async {
                          final d = await showDatePicker(
                              context: ctx,
                              initialDate: start,
                              firstDate: DateTime(2020),
                              lastDate: DateTime(2100));
                          if (d != null) setState(() => start = d);
                        }),
                    ListTile(
                        title: Text(
                            'End: ${end.toLocal().toString().split(' ').first}'),
                        onTap: () async {
                          final d = await showDatePicker(
                              context: ctx,
                              initialDate: end,
                              firstDate: DateTime(2020),
                              lastDate: DateTime(2100));
                          if (d != null)
                            setState(() =>
                                end = DateTime(d.year, d.month, d.day, 23, 59));
                        }),
                  ])),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Cancel')),
                    FilledButton(
                        onPressed: () => Navigator.pop(ctx, true),
                        child: const Text('Save')),
                  ],
                )));
    if (ok != true || category == null) return;
    final value = double.tryParse(amount.text.trim());
    if (name.text.trim().isEmpty ||
        value == null ||
        value <= 0 ||
        end.isBefore(start)) {
      _error('Enter a valid name, positive amount and date range.');
      return;
    }
    try {
      if (budget == null) {
        await _service.create(
            categoryId: category!,
            name: name.text,
            amount: value,
            start: start,
            end: end);
      } else {
        await _service.update(budget.id,
            categoryId: category,
            name: name.text,
            amount: value,
            start: start,
            end: end);
      }
      if (mounted) setState(_load);
    } catch (e) {
      if (mounted) _error(e);
    }
  }

  void _error(Object e) {
    final m = e is ApiException ? e.userMessage : 'Could not save budget.';
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(m)));
  }

  Future<void> _delete(Budget b) async {
    final ok = await showDialog<bool>(
        context: context,
        builder: (c) => AlertDialog(
                title: const Text('Deactivate budget?'),
                content: Text(b.name),
                actions: [
                  TextButton(
                      onPressed: () => Navigator.pop(c, false),
                      child: const Text('Cancel')),
                  FilledButton(
                      onPressed: () => Navigator.pop(c, true),
                      child: const Text('Deactivate'))
                ]));
    if (ok != true) return;
    try {
      await _service.delete(b.id);
      if (mounted) setState(_load);
    } catch (e) {
      if (mounted) _error(e);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(title: const Text('Budgets'), actions: [
        IconButton(onPressed: _refresh, icon: const Icon(Icons.refresh))
      ]),
      body: FutureBuilder<List<Budget>>(
          future: _future,
          builder: (c, s) {
            if (s.connectionState != ConnectionState.done)
              return const Center(child: CircularProgressIndicator());
            if (s.hasError)
              return Center(
                  child: FilledButton(
                      onPressed: _refresh, child: const Text('Retry')));
            final items = s.data!.where((b) => b.active).toList();
            return RefreshIndicator(
                onRefresh: _refresh,
                child: ListView(padding: const EdgeInsets.all(16), children: [
                  if (items.isEmpty)
                    const Card(
                        child: Padding(
                            padding: EdgeInsets.all(20),
                            child: Text(
                                'No budgets yet. Create a category budget to track spending.'))),
                  ...items.map(_card),
                  const SizedBox(height: 12),
                  FilledButton.icon(
                      onPressed: () => _edit(),
                      icon: const Icon(Icons.add),
                      label: const Text('Add budget')),
                ]));
          }));

  Widget _card(Budget b) => FutureBuilder<BudgetProgress>(
      future: _service.progress(b.id),
      builder: (c, s) {
        final p = s.data;
        final ratio = p == null
            ? 0
            : (p.budgetAmount == 0
                ? 0
                : (p.spent / p.budgetAmount).clamp(0, 1).toDouble());
        return Card(
            child: ListTile(
          title: Text(b.name),
          subtitle: Text(
              '₹${p?.spent.toStringAsFixed(2) ?? '...'} / ₹${b.amount.toStringAsFixed(2)} · ${b.start.toLocal().toString().split(' ').first} to ${b.end.toLocal().toString().split(' ').first}'),
          trailing: PopupMenuButton<String>(
            onSelected: (v) {
              if (v == 'edit') _edit(budget: b);
              if (v == 'delete') _delete(b);
            },
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'edit', child: Text('Edit')),
              PopupMenuItem(value: 'delete', child: Text('Deactivate'))
            ],
            child: SizedBox(
                width: 70,
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      LinearProgressIndicator(value: ratio),
                      const SizedBox(height: 4),
                      Text(p == null
                          ? ''
                          : p.overBudget
                              ? 'Over budget'
                              : '${p.percentage.toStringAsFixed(0)}%')
                    ])),
          ),
        ));
      });
}
