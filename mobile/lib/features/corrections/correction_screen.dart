import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'correction_service.dart';

class CorrectionScreen extends StatefulWidget {
  const CorrectionScreen({super.key, this.transactionId});
  final int? transactionId;
  @override
  State<CorrectionScreen> createState() => _CorrectionScreenState();
}

class _CorrectionScreenState extends State<CorrectionScreen> {
  final _text = TextEditingController();
  final _service = CorrectionService();
  bool _busy = false;
  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final t = _text.text.trim();
    if (t.isEmpty || _busy) return;
    setState(() => _busy = true);
    try {
      final r = await _service.submit(t, transactionId: widget.transactionId);
      if (!mounted) return;
      if (r.status == 'CORRECTED') {
        _saved(r);
      } else {
        await _review(r);
      }
    } catch (e) {
      if (mounted) _error(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _review(CorrectionResult r) async {
    final c = r.candidate;
    final ok = await showDialog<bool>(
        context: context,
        builder: (_) => AlertDialog(
              title: const Text('Review correction'),
              content: SingleChildScrollView(
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                    Text('Action: ${c.action ?? 'Unknown'}'),
                    if (c.transactionId != null)
                      Text('Transaction: #${c.transactionId}'),
                    if (c.reimbursementId != null)
                      Text('Reimbursement: #${c.reimbursementId}'),
                    if (c.amount != null) Text('Amount: ₹${c.amount}'),
                    if (c.transactionDate != null)
                      Text('Date: ${c.transactionDate}'),
                    if (c.description != null)
                      Text('Description: ${c.description}'),
                    if (c.accountName != null)
                      Text('Account: ${c.accountName}'),
                    if (c.categoryName != null)
                      Text('Category: ${c.categoryName}'),
                    if (c.reason != null)
                      Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(c.reason!)),
                    if (c.missing.isNotEmpty)
                      Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text('Missing: ${c.missing.join(', ')}')),
                  ])),
              actions: [
                TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: const Text('Cancel')),
                if (c.missing.isEmpty)
                  FilledButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: const Text('Confirm'))
              ],
            ));
    if (ok != true || !mounted) return;
    setState(() => _busy = true);
    try {
      final saved = await _service.submit(c.text, confirm: true, candidate: c);
      if (mounted) _saved(saved);
    } catch (e) {
      if (mounted) _error(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _saved(CorrectionResult r) {
    _text.clear();
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Correction saved and added to history.')));
  }

  void _error(Object e) {
    final m = e is ApiException
        ? e.userMessage
        : 'Could not apply correction. Please try again.';
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(m)));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(title: const Text('Correct financial record')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        const Card(
            child: Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                    'Describe the correction in plain language. The app reviews the interpreted change before saving it.'))),
        const SizedBox(height: 16),
        TextField(
            controller: _text,
            minLines: 3,
            maxLines: 5,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
                labelText: 'What should be corrected?',
                hintText: 'Change transaction 42 amount to ₹550',
                border: OutlineInputBorder())),
        const SizedBox(height: 12),
        FilledButton.icon(
            onPressed: _busy ? null : _submit,
            icon: _busy
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.check),
            label: const Text('Review correction'))
      ]));
}
