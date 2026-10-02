// ignore_for_file: prefer_interpolation_to_compose_strings, use_build_context_synchronously
import 'package:flutter/material.dart';
import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../data/credit_api.dart';

class CreditPage extends StatefulWidget {
  const CreditPage({required this.accessToken, super.key});
  final String accessToken;
  @override
  State<CreditPage> createState() => _CreditPageState();
}

class _CreditPageState extends State<CreditPage> {
  late final CreditApi api;
  List<CreditCardSummary> cards = [];
  bool loading = true;
  String? error;
  @override
  void initState() {
    super.initState();
    api = CreditApi(config: AppEnvironmentConfig.development);
    load();
  }

  Future<void> load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final x = await api.list(widget.accessToken);
      if (mounted) setState(() => cards = x);
    } catch (e) {
      if (mounted) {
        setState(
          () => error = e is AppException
              ? e.message
              : 'Unable to load credit cards.',
        );
      }
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  String money(double v) => '₹ ' + v.toStringAsFixed(2);
  Future<void> configure(CreditCardSummary card) async {
    final limitController = TextEditingController(
      text: card.limit.toStringAsFixed(2),
    );
    final statementController = TextEditingController(
      text: card.statementDay.toString(),
    );
    final dueController = TextEditingController(text: card.dueDay.toString());

    final ok = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheet) => StatefulBuilder(
        builder: (sheet, setSheet) {
          var saving = false;

          Future<void> submit() async {
            if (saving) return;

            final limit = double.tryParse(limitController.text);
            final statementDay = int.tryParse(statementController.text);
            final dueDay = int.tryParse(dueController.text);

            if (limit == null ||
                limit <= 0 ||
                statementDay == null ||
                dueDay == null ||
                statementDay < 1 ||
                statementDay > 31 ||
                dueDay < 1 ||
                dueDay > 31) {
              ScaffoldMessenger.of(sheet).showSnackBar(
                const SnackBar(content: Text('Enter valid credit settings.')),
              );
              return;
            }

            setSheet(() => saving = true);

            try {
              await api.configure(
                widget.accessToken,
                card.accountId,
                limit: limit,
                statementDay: statementDay,
                dueDay: dueDay,
              );
              if (sheet.mounted) Navigator.pop(sheet, true);
            } catch (e) {
              if (sheet.mounted) setSheet(() => saving = false);
              if (sheet.mounted) {
                ScaffoldMessenger.of(sheet).showSnackBar(
                  SnackBar(
                    content: Text(
                      e is AppException
                          ? e.message
                          : 'Unable to save settings.',
                    ),
                  ),
                );
              }
            }
          }

          return PopScope(
            canPop: !saving,
            child: Padding(
              padding: EdgeInsets.fromLTRB(
                20,
                12,
                20,
                MediaQuery.viewInsetsOf(sheet).bottom + 20,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Configure ' + card.name,
                    style: Theme.of(sheet).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: limitController,
                    enabled: !saving,
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    decoration: const InputDecoration(
                      labelText: 'Credit limit',
                      prefixText: '₹ ',
                    ),
                  ),
                  TextField(
                    controller: statementController,
                    enabled: !saving,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Statement day (1-31)',
                    ),
                  ),
                  TextField(
                    controller: dueController,
                    enabled: !saving,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Payment due day (1-31)',
                    ),
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: saving ? null : submit,
                    icon: saving
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.check),
                    label: Text(saving ? 'Saving...' : 'Save settings'),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );

    limitController.dispose();
    statementController.dispose();
    dueController.dispose();

    if (ok == true) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Credit settings saved.')));
      }
      await load();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: load,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(20, 18, 20, 100),
          children: [
            Text('Credit', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 6),
            const Text('Credit cards, outstanding balance and payment dates'),
            const SizedBox(height: 16),
            if (loading && cards.isEmpty)
              const Center(child: CircularProgressIndicator())
            else if (error != null && cards.isEmpty)
              _error(context)
            else if (cards.isEmpty)
              _empty(context)
            else
              ...cards.map((card) => _card(context, card)),
          ],
        ),
      ),
    );
  }

  Widget _error(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Text(error!, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: load,
            icon: const Icon(Icons.refresh),
            label: const Text('Retry'),
          ),
        ],
      ),
    ),
  );
  Widget _empty(BuildContext context) => const Card(
    child: Padding(
      padding: EdgeInsets.all(24),
      child: Column(
        children: [
          Icon(Icons.credit_card, size: 48),
          SizedBox(height: 10),
          Text('No configured credit cards'),
          SizedBox(height: 8),
          Text(
            'Create a Credit Card account in Accounts, then configure it here.',
            textAlign: TextAlign.center,
          ),
        ],
      ),
    ),
  );
  Widget _card(BuildContext context, CreditCardSummary card) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.credit_card),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  card.name,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              IconButton(
                onPressed: () => configure(card),
                icon: const Icon(Icons.settings_outlined),
              ),
            ],
          ),
          if (card.institution != null) Text(card.institution!),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _metric('Outstanding', money(card.outstanding))),
              Expanded(child: _metric('Available', money(card.available))),
            ],
          ),
          const SizedBox(height: 12),
          LinearProgressIndicator(value: (card.utilization / 100).clamp(0, 1)),
          const SizedBox(height: 6),
          Text(
            'Utilization ' +
                card.utilization.toStringAsFixed(2) +
                '% • Limit ' +
                money(card.limit),
          ),
          const SizedBox(height: 8),
          Text(
            'Statement day ' +
                card.statementDay.toString() +
                ' • Due day ' +
                card.dueDay.toString() +
                ' • Next due ' +
                card.nextDue.day.toString() +
                '/' +
                card.nextDue.month.toString() +
                '/' +
                card.nextDue.year.toString(),
          ),
          if (card.overLimit > 0)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'Over limit: ' + money(card.overLimit),
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
        ],
      ),
    ),
  );
  Widget _metric(String label, String value) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(label),
      const SizedBox(height: 3),
      Text(
        value,
        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
      ),
    ],
  );
}
