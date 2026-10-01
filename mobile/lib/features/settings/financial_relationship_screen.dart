import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'financial_relationship_service.dart';

class FinancialRelationshipScreen extends StatefulWidget {
  const FinancialRelationshipScreen({super.key});
  @override
  State<FinancialRelationshipScreen> createState() =>
      _FinancialRelationshipScreenState();
}

class _FinancialRelationshipScreenState
    extends State<FinancialRelationshipScreen> {
  final _text = TextEditingController();
  final _service = FinancialRelationshipService();
  bool _busy = false;

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  String _intent(String? value) {
    switch (value) {
      case 'LEND':
        return 'Money you lent';
      case 'BORROW':
        return 'Money you borrowed';
      case 'REPAY_BORROWED':
        return 'Borrowed money repayment';
      case 'RECEIVE_LENT_REPAYMENT':
        return 'Lent money repayment';
      default:
        return value?.replaceAll('_', ' ') ?? 'Financial relationship';
    }
  }

  Future<void> _submit() async {
    final text = _text.text.trim();
    if (text.isEmpty || _busy) return;
    setState(() => _busy = true);
    try {
      final result = await _service.submit(text);
      if (!mounted) return;
      if (result.status == 'SAVED') {
        _showSaved(result);
      } else {
        await _confirmCandidate(result);
      }
    } catch (e) {
      if (mounted) _showError(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _confirmCandidate(RelationshipResult result) async {
    final c = result.candidate;
    final details = <Widget>[
      Text(_intent(c.intent), style: Theme.of(context).textTheme.titleMedium),
      if (c.amount != null) Text('Amount: ₹' + c.amount!),
      if (c.personName != null) Text('Person: ' + c.personName!),
      if (c.accountName != null) Text('Account: ' + c.accountName!),
      if (c.reason != null)
        Padding(padding: const EdgeInsets.only(top: 8), child: Text(c.reason!)),
      if (c.missing.isNotEmpty)
        Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text('Missing: ' + c.missing.join(', '))),
      const SizedBox(height: 12),
      Text(c.missing.isEmpty
          ? 'Save this relationship?'
          : 'More information is required before it can be saved.'),
    ];
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Confirm relationship'),
        content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: details),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel')),
          if (c.missing.isEmpty)
            FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Confirm')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    setState(() => _busy = true);
    try {
      final saved = await _service.submit(c.text, confirm: true, candidate: c);
      if (mounted) _showSaved(saved);
    } catch (e) {
      if (mounted) _showError(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _showSaved(RelationshipResult result) {
    final c = result.candidate;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(c.personName == null
          ? 'Financial relationship saved.'
          : _intent(c.intent) + ' for ' + c.personName! + ' saved.'),
    ));
    _text.clear();
  }

  void _showError(Object error) {
    final message = error is ApiException
        ? error.userMessage
        : 'Could not save this relationship. Please try again.';
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Lending & borrowing')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Card(
                child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                        'Describe what happened in plain language. For example: “I lent ₹5,000 to Ravi from HDFC” or “I borrowed ₹2,000 from Gagan”. The app will show what it understood before saving.'))),
            const SizedBox(height: 16),
            TextField(
              controller: _text,
              minLines: 3,
              maxLines: 5,
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                labelText: 'What happened?',
                hintText: 'I lent ₹5,000 to Ravi from HDFC',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: _busy ? null : _submit,
              icon: _busy
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.check),
              label: const Text('Review & save'),
            ),
          ],
        ),
      );
}
