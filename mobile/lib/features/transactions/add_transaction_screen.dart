import 'package:flutter/material.dart';
import 'transaction_data.dart';
import 'transaction_service.dart';
import '../settings/manage_finances_screen.dart';

class AddTransactionScreen extends StatefulWidget {
  const AddTransactionScreen({super.key});
  @override
  State<AddTransactionScreen> createState() => _AddTransactionScreenState();
}

class _AddTransactionScreenState extends State<AddTransactionScreen> {
  final _service = TransactionService();
  final _amount = TextEditingController();
  final _description = TextEditingController();
  List<AccountOption> _accounts = [];
  List<CategoryOption> _categories = [];
  TransactionType _type = TransactionType.expense;
  int? _accountId, _categoryId, _transferAccountId;
  DateTime _date = DateTime.now();
  bool _loading = true, _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _amount.dispose();
    _description.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final results =
          await Future.wait([_service.accounts(), _service.categories()]);
      if (!mounted) return;
      setState(() {
        _accounts = results[0] as List<AccountOption>;
        _categories = results[1] as List<CategoryOption>;
        _loading = false;
      });
    } catch (e) {
      if (mounted)
        setState(() {
          _loading = false;
          _error = e.toString();
        });
    }
  }

  List<CategoryOption> get _filteredCategories {
    final wanted = _type == TransactionType.income ? 'INCOME' : 'EXPENSE';
    return _categories
        .where((c) => c.type == wanted && c.type.isNotEmpty)
        .toList();
  }

  String _label(TransactionType type) => switch (type) {
        TransactionType.income => 'Income',
        TransactionType.expense => 'Expense',
        TransactionType.transfer => 'Transfer',
        TransactionType.refund => 'Refund',
      };

  Future<void> _save() async {
    final amount = double.tryParse(_amount.text.trim());
    if (_accountId == null || amount == null || amount <= 0) {
      setState(() => _error = 'Select an account and enter a valid amount.');
      return;
    }
    if (_type == TransactionType.transfer && _transferAccountId == null) {
      setState(() => _error = 'Select the destination account.');
      return;
    }
    if (_type != TransactionType.transfer &&
        _filteredCategories.isNotEmpty &&
        _categoryId == null) {
      setState(() => _error = 'Select a category.');
      return;
    }
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await _service.create(TransactionPayload(
          accountId: _accountId!,
          type: _type,
          amount: amount,
          date: _date,
          categoryId: _type == TransactionType.transfer ? null : _categoryId,
          transferAccountId:
              _type == TransactionType.transfer ? _transferAccountId : null,
          description: _description.text));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('${_label(_type)} added successfully')));
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted)
        setState(() {
          _saving = false;
          _error =
              e is Exception ? e.toString() : 'Could not save transaction.';
        });
    }
  }

  Future<void> _openSetup() async {
    await Navigator.push(context,
        MaterialPageRoute(builder: (_) => const ManageFinancesScreen()));
    if (mounted) {
      setState(() {
        _loading = true;
        _error = null;
      });
      _load();
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Add Transaction')),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : ListView(padding: const EdgeInsets.all(20), children: [
                if (_accounts.isEmpty)
                  Card(
                      child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('One small setup first',
                                    style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.w600)),
                                const SizedBox(height: 6),
                                const Text(
                                    'Add a cash, bank, card or wallet account before recording a transaction.'),
                                const SizedBox(height: 10),
                                OutlinedButton.icon(
                                    onPressed: _openSetup,
                                    icon: const Icon(
                                        Icons.account_balance_wallet),
                                    label: const Text('Set up accounts')),
                              ]))),
                if (_accounts.isEmpty) const SizedBox(height: 12),
                SegmentedButton<TransactionType>(
                    segments: TransactionType.values
                        .map((t) =>
                            ButtonSegment(value: t, label: Text(_label(t))))
                        .toList(),
                    selected: {_type},
                    onSelectionChanged: (v) => setState(() {
                          _type = v.first;
                          _categoryId = null;
                          _transferAccountId = null;
                        })),
                const SizedBox(height: 20),
                TextField(
                    controller: _amount,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                        labelText: 'Amount',
                        prefixText: '₹ ',
                        border: OutlineInputBorder())),
                const SizedBox(height: 12),
                DropdownButtonFormField<int>(
                    value: _accountId,
                    decoration: const InputDecoration(
                        labelText: 'Account', border: OutlineInputBorder()),
                    items: _accounts
                        .where((a) => a.type.isNotEmpty)
                        .map((a) =>
                            DropdownMenuItem(value: a.id, child: Text(a.name)))
                        .toList(),
                    onChanged: (v) => setState(() => _accountId = v)),
                const SizedBox(height: 12),
                if (_type != TransactionType.transfer &&
                    _filteredCategories.isEmpty)
                  Card(
                      child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Row(children: [
                            const Expanded(
                                child: Text(
                                    'No matching categories yet. You can add one from Accounts & categories.')),
                            TextButton(
                                onPressed: _openSetup, child: const Text('Add'))
                          ]))),
                if (_type == TransactionType.transfer)
                  DropdownButtonFormField<int>(
                      value: _transferAccountId,
                      decoration: const InputDecoration(
                          labelText: 'Transfer to',
                          border: OutlineInputBorder()),
                      items: _accounts
                          .where((a) => a.id != _accountId)
                          .map((a) => DropdownMenuItem(
                              value: a.id, child: Text(a.name)))
                          .toList(),
                      onChanged: (v) => setState(() => _transferAccountId = v))
                else if (_filteredCategories.isNotEmpty)
                  DropdownButtonFormField<int>(
                      value: _categoryId,
                      decoration: InputDecoration(
                          labelText: _type == TransactionType.income
                              ? 'Income category'
                              : 'Expense category',
                          border: const OutlineInputBorder()),
                      items: _filteredCategories
                          .map((c) => DropdownMenuItem(
                              value: c.id, child: Text(c.name)))
                          .toList(),
                      onChanged: (v) => setState(() => _categoryId = v)),
                const SizedBox(height: 12),
                TextField(
                    controller: _description,
                    maxLines: 2,
                    decoration: const InputDecoration(
                        labelText: 'Description',
                        border: OutlineInputBorder())),
                const SizedBox(height: 12),
                ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Date'),
                    subtitle: Text('${_date.day}/${_date.month}/${_date.year}'),
                    trailing: const Icon(Icons.calendar_today),
                    onTap: () async {
                      final d = await showDatePicker(
                          context: context,
                          firstDate: DateTime(2000),
                          lastDate: DateTime.now(),
                          initialDate: _date);
                      if (d != null)
                        setState(() => _date = DateTime(
                            d.year, d.month, d.day, _date.hour, _date.minute));
                    }),
                if (_error != null)
                  Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(_error!,
                          style: const TextStyle(color: Colors.red))),
                FilledButton.icon(
                    onPressed: _saving ? null : _save,
                    icon: _saving
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2))
                        : const Icon(Icons.save),
                    label: Text(_saving ? 'Saving…' : 'Save ${_label(_type)}')),
              ]),
      );
}
