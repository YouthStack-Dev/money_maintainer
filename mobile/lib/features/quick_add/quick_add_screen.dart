import 'package:flutter/material.dart';
import 'quick_entry_data.dart';
import 'quick_entry_service.dart';

class QuickAddScreen extends StatefulWidget {
  const QuickAddScreen({super.key});
  @override State<QuickAddScreen> createState() => _QuickAddScreenState();
}

class _QuickAddScreenState extends State<QuickAddScreen> {
  final _controller = TextEditingController();
  final _service = QuickEntryService();
  bool _loading = false;
  QuickEntryResult? _result;
  String? _error;

  @override void dispose() { _controller.dispose(); super.dispose(); }

  Future<void> _submit() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;
    setState(() { _loading = true; _error = null; _result = null; });
    try {
      final result = await _service.submit(text);
      if (mounted) setState(() { _result = result; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _loading = false; _error = 'Could not process this entry. Please try again.'; });
    }
  }

  String _money(double? value) => value == null ? '—' : '₹${value.toStringAsFixed(0)}';

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Quick Add')),
    body: ListView(padding: const EdgeInsets.all(20), children: [
      Text('What happened?', style: Theme.of(context).textTheme.headlineSmall),
      const SizedBox(height: 8),
      const Text('Try: 110 petrol · salary 29800 · 7000 lending Giri'),
      const SizedBox(height: 16),
      TextField(
        controller: _controller, minLines: 3, maxLines: 6,
        textInputAction: TextInputAction.done, onSubmitted: (_) => _submit(),
        decoration: const InputDecoration(hintText: 'Type what happened with your money…', border: OutlineInputBorder()),
      ),
      const SizedBox(height: 12),
      FilledButton.icon(
        onPressed: _loading ? null : _submit,
        icon: _loading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.add),
        label: Text(_loading ? 'Processing…' : 'Add'),
      ),
      if (_error != null) ...[const SizedBox(height: 16), Text(_error!, style: TextStyle(color: Colors.red))],
      if (_result != null) ...[
        const SizedBox(height: 24),
        Text(_result!.status, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        ..._result!.candidates.map((c) => Card(child: ListTile(
          title: Text(c.description?.isNotEmpty == true ? c.description! : c.text),
          subtitle: Text([
            if (c.transactionType != null) c.transactionType!,
            if (c.categoryName != null) c.categoryName!,
            if (c.accountName != null) c.accountName!,
            if (c.missing.isNotEmpty) 'Needs: ${c.missing.join(', ')}',
          ].join(' · ')),
          trailing: Text(_money(c.amount)),
        ))),
      ],
    ]),
  );
}
