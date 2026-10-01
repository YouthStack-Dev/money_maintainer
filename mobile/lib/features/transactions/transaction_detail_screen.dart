import 'package:flutter/material.dart';
import 'transaction_data.dart';
import 'transaction_service.dart';
import 'edit_transaction_screen.dart';
import '../corrections/correction_screen.dart';

class TransactionDetailScreen extends StatefulWidget {
  const TransactionDetailScreen({super.key, required this.id});
  final int id;
  @override
  State<TransactionDetailScreen> createState() =>
      _TransactionDetailScreenState();
}

class _TransactionDetailScreenState extends State<TransactionDetailScreen> {
  final _service = TransactionService();
  TransactionRecord? _tx;
  bool _loading = true, _deleting = false;
  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final x = await _service.get(widget.id);
      if (mounted) setState(() => _tx = x);
    } catch (e) {
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _edit() async {
    if (_tx == null) return;
    final r = await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (_) => EditTransactionScreen(transaction: _tx!)));
    if (r == true && mounted) _load();
  }

  Future<void> _delete() async {
    final ok = await showDialog<bool>(
        context: context,
        builder: (c) => AlertDialog(
                title: const Text('Delete transaction?'),
                content: const Text(
                    'This will deactivate the transaction. Existing history is kept safe.'),
                actions: [
                  TextButton(
                      onPressed: () => Navigator.pop(c, false),
                      child: const Text('Cancel')),
                  FilledButton(
                      onPressed: () => Navigator.pop(c, true),
                      child: const Text('Delete'))
                ]));
    if (ok != true) return;
    setState(() => _deleting = true);
    try {
      await _service.delete(widget.id);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _deleting = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  String _date(DateTime d) => '${d.day}/${d.month}/${d.year}';
  @override
  Widget build(BuildContext c) {
    final x = _tx;
    return Scaffold(
        appBar: AppBar(title: const Text('Transaction details')),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : x == null
                ? const Center(child: Text('Unable to load transaction.'))
                : ListView(padding: const EdgeInsets.all(20), children: [
                    Center(child: Text(x.type.name.toUpperCase())),
                    const SizedBox(height: 8),
                    Center(
                        child: Text('₹${x.amount.toStringAsFixed(2)}',
                            style: Theme.of(c).textTheme.headlineMedium)),
                    const SizedBox(height: 24),
                    Text(
                        'Description: ${x.description?.isNotEmpty == true ? x.description : 'No description'}'),
                    Text('Date: ${_date(x.date)}'),
                    Text('Account: #${x.accountId}'),
                    if (x.categoryId != null)
                      Text('Category: #${x.categoryId}'),
                    if (x.transferAccountId != null)
                      Text('Transfer to: #${x.transferAccountId}'),
                    Text('Status: ${x.active ? 'Active' : 'Inactive'}'),
                    const SizedBox(height: 28),
                    FilledButton.icon(
                        onPressed: _deleting || !x.active ? null : _edit,
                        icon: const Icon(Icons.edit),
                        label: const Text('Edit transaction')),
                    const SizedBox(height: 10),
                    OutlinedButton.icon(
                        onPressed: _deleting || !x.active
                            ? null
                            : () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (_) =>
                                        CorrectionScreen(transactionId: x.id))),
                        icon: const Icon(Icons.build_outlined),
                        label: const Text('Correct financial record')),
                    const SizedBox(height: 10),
                    OutlinedButton.icon(
                        onPressed: _deleting || !x.active ? null : _delete,
                        icon: const Icon(Icons.delete_outline),
                        label: Text(
                            _deleting ? 'Deleting...' : 'Delete transaction'))
                  ]));
  }
}
