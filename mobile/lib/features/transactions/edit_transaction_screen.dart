import 'package:flutter/material.dart';
import 'transaction_data.dart';
import 'transaction_service.dart';

class EditTransactionScreen extends StatefulWidget {
  const EditTransactionScreen({super.key, required this.transaction});
  final TransactionRecord transaction;
  @override
  State<EditTransactionScreen> createState() => _EditTransactionScreenState();
}

class _EditTransactionScreenState extends State<EditTransactionScreen> {
  final _service = TransactionService();
  late TextEditingController _amount, _description;
  late int _account;
  late DateTime _date;
  late TransactionType _type;
  int? _category, _transfer;
  List<AccountOption> _accounts = [];
  List<CategoryOption> _categories = [];
  bool _loading = true, _saving = false;
  String? _error;
  @override
  void initState() {
    super.initState();
    final t = widget.transaction;
    _amount = TextEditingController(text: t.amount.toStringAsFixed(2));
    _description = TextEditingController(text: t.description ?? '');
    _account = t.accountId;
    _date = t.date;
    _type = t.type;
    _category = t.categoryId;
    _transfer = t.transferAccountId;
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
      final r = await Future.wait([_service.accounts(), _service.categories()]);
      if (mounted)
        setState(() {
          _accounts = r[0] as List<AccountOption>;
          _categories = r[1] as List<CategoryOption>;
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

  List<CategoryOption> get _cats {
    final w = _type == TransactionType.income ? 'INCOME' : 'EXPENSE';
    return _categories.where((c) => c.type == w).toList();
  }

  String _label(TransactionType t) => switch (t) {
        TransactionType.income => 'Income',
        TransactionType.expense => 'Expense',
        TransactionType.transfer => 'Transfer',
        TransactionType.refund => 'Refund'
      };
  Future<void> _save() async {
    final amount = double.tryParse(_amount.text.trim());
    if (amount == null || amount <= 0) {
      setState(() => _error = 'Enter a valid amount.');
      return;
    }
    if (_type == TransactionType.transfer &&
        (_transfer == null || _transfer == _account)) {
      setState(() => _error = 'Select a different destination account.');
      return;
    }
    if (_type != TransactionType.transfer &&
        _cats.isNotEmpty &&
        _category == null) {
      setState(() => _error = 'Select a category.');
      return;
    }
    setState(() => _saving = true);
    try {
      await _service.update(
          widget.transaction.id,
          TransactionPayload(
              accountId: _account,
              type: _type,
              amount: amount,
              date: _date,
              categoryId: _type == TransactionType.transfer ? null : _category,
              transferAccountId:
                  _type == TransactionType.transfer ? _transfer : null,
              description: _description.text));
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext c) => Scaffold(
      appBar: AppBar(title: const Text('Edit transaction')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(padding: const EdgeInsets.all(20), children: [
              SegmentedButton<TransactionType>(
                  segments: TransactionType.values
                      .map((t) =>
                          ButtonSegment(value: t, label: Text(_label(t))))
                      .toList(),
                  selected: {_type},
                  onSelectionChanged: (v) => setState(() {
                        _type = v.first;
                        _category = null;
                        _transfer = null;
                      })),
              const SizedBox(height: 16),
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
                  initialValue:
                      _accounts.any((a) => a.id == _account) ? _account : null,
                  decoration: const InputDecoration(
                      labelText: 'Account', border: OutlineInputBorder()),
                  items: _accounts
                      .map((a) =>
                          DropdownMenuItem(value: a.id, child: Text(a.name)))
                      .toList(),
                  onChanged: (v) => setState(() => _account = v!)),
              const SizedBox(height: 12),
              if (_type == TransactionType.transfer)
                DropdownButtonFormField<int>(
                    initialValue: _accounts.any((a) => a.id == _transfer)
                        ? _transfer
                        : null,
                    decoration: const InputDecoration(
                        labelText: 'Transfer to', border: OutlineInputBorder()),
                    items: _accounts
                        .where((a) => a.id != _account)
                        .map((a) =>
                            DropdownMenuItem(value: a.id, child: Text(a.name)))
                        .toList(),
                    onChanged: (v) => setState(() => _transfer = v))
              else if (_cats.isNotEmpty)
                DropdownButtonFormField<int>(
                    initialValue:
                        _cats.any((x) => x.id == _category) ? _category : null,
                    decoration: const InputDecoration(
                        labelText: 'Category', border: OutlineInputBorder()),
                    items: _cats
                        .map((x) =>
                            DropdownMenuItem(value: x.id, child: Text(x.name)))
                        .toList(),
                    onChanged: (v) => setState(() => _category = v)),
              const SizedBox(height: 12),
              TextField(
                  controller: _description,
                  maxLines: 2,
                  decoration: const InputDecoration(
                      labelText: 'Description', border: OutlineInputBorder())),
              const SizedBox(height: 12),
              ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Date'),
                  subtitle: Text('${_date.day}/${_date.month}/${_date.year}'),
                  trailing: const Icon(Icons.calendar_today),
                  onTap: () async {
                    final d = await showDatePicker(
                        context: c,
                        firstDate: DateTime(2000),
                        lastDate: DateTime.now(),
                        initialDate: _date);
                    if (d != null)
                      setState(() => _date = DateTime(
                          d.year, d.month, d.day, _date.hour, _date.minute));
                  }),
              if (_error != null)
                Text(_error!, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 12),
              FilledButton.icon(
                  onPressed: _saving ? null : _save,
                  icon: const Icon(Icons.save),
                  label: Text(_saving ? 'Saving...' : 'Save changes'))
            ]));
}
