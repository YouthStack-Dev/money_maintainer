import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'conversational_finance_service.dart';

class ConversationalFinanceScreen extends StatefulWidget {
  const ConversationalFinanceScreen({super.key});
  @override
  State<ConversationalFinanceScreen> createState() =>
      _ConversationalFinanceScreenState();
}

class _ConversationalFinanceScreenState
    extends State<ConversationalFinanceScreen> {
  final _input = TextEditingController();
  final _service = ConversationalFinanceService();
  ConversationResult? _result;
  bool _busy = false;
  @override
  void dispose() {
    _input.dispose();
    super.dispose();
  }

  Future<void> _ask([String? preset]) async {
    final text = (preset ?? _input.text).trim();
    if (text.isEmpty || _busy) return;
    _input.text = text;
    setState(() => _busy = true);
    try {
      final r = await _service.ask(text, context: _result?.context);
      if (mounted) setState(() => _result = r);
    } catch (e) {
      if (mounted) _error(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _error(Object e) {
    final m =
        e is ApiException ? e.userMessage : 'Could not answer that question.';
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(m)));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(title: const Text('Finance assistant')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        const Card(
            child: Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                    'Ask about spending, savings, budgets, debts, cards or net worth in plain language.'))),
        if (_result != null) ...[
          _answerCard(_result!),
          const SizedBox(height: 12),
          if (_result!.followUp.isNotEmpty)
            Text('Try next', style: Theme.of(context).textTheme.titleMedium),
          ..._result!.followUp.map((q) => TextButton.icon(
              onPressed: _busy ? null : () => _ask(q),
              icon: const Icon(Icons.arrow_forward),
              label: Text(q)))
        ],
        const SizedBox(height: 12),
        TextField(
            controller: _input,
            minLines: 2,
            maxLines: 4,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(
                labelText: 'Ask your finance question',
                hintText: 'How much did I spend this month?',
                border: OutlineInputBorder())),
        const SizedBox(height: 12),
        FilledButton.icon(
            onPressed: _busy ? null : _ask,
            icon: _busy
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.send),
            label: const Text('Ask'))
      ]));
  Widget _answerCard(ConversationResult r) => Card(
      child: Padding(
          padding: const EdgeInsets.all(16),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(r.intent.replaceAll('_', ' '),
                style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Text(r.answer),
            if (r.data.isNotEmpty)
              Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Text(r.data.entries
                      .map((e) => '${e.key}: ${e.value}')
                      .join('\n')))
          ])));
}
