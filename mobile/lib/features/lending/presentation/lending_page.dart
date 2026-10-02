// ignore_for_file: prefer_interpolation_to_compose_strings, curly_braces_in_flow_control_structures, use_build_context_synchronously
import 'package:flutter/material.dart';
import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../data/lending_api.dart';

class LendingPage extends StatefulWidget {
  const LendingPage({required this.accessToken, super.key});
  final String accessToken;
  @override
  State<LendingPage> createState() => _LendingPageState();
}

class _LendingPageState extends State<LendingPage> {
  late final LendingApi api;
  List<LendingItem> items = [];
  LendingSummary? summary;
  List<LendingAccount> accounts = [];
  bool loading = true;
  bool _operationInProgress = false;
  String? error;
  int filter = 0;
  @override
  void initState() {
    super.initState();
    api = LendingApi(config: AppEnvironmentConfig.development);
    load();
  }

  Future<void> load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final r = await Future.wait([
        api.list(widget.accessToken),
        api.summary(widget.accessToken),
        api.accounts(widget.accessToken),
      ]);
      if (mounted)
        setState(() {
          items = r[0] as List<LendingItem>;
          summary = r[1] as LendingSummary;
          accounts = r[2] as List<LendingAccount>;
        });
    } catch (e) {
      if (mounted)
        setState(
          () =>
              error = e is AppException ? e.message : 'Unable to load lending.',
        );
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  String money(double v) => '₹ ' + v.toStringAsFixed(2);
  List<LendingItem> get visible => items
      .where(
        (x) =>
            filter == 0 ||
            (filter == 1 && x.direction == 'LENT') ||
            (filter == 2 && x.direction == 'BORROWED'),
      )
      .toList();

  Future<void> addRecord(String direction) async {
    if (_operationInProgress) return;
    if (accounts.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Add an active account first.')),
      );
      return;
    }
    setState(() => _operationInProgress = true);
    final person = TextEditingController(),
        amount = TextEditingController(),
        note = TextEditingController();
    int accountId = accounts.first.id;
    DateTime? due;
    var saving = false;
    final saved = await showModalBottomSheet<LendingItem?>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheet) => StatefulBuilder(
        builder: (sheet, setSheet) => Padding(
          padding: EdgeInsets.fromLTRB(
            20,
            12,
            20,
            MediaQuery.viewInsetsOf(sheet).bottom + 20,
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  direction == 'LENT' ? 'Lend money' : 'Borrowed money',
                  style: Theme.of(sheet).textTheme.headlineSmall,
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: person,
                  enabled: !saving,
                  decoration: const InputDecoration(
                    labelText: 'Person name',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: amount,
                  enabled: !saving,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Amount',
                    prefixText: '₹ ',
                  ),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<int>(
                  key: ValueKey(
                    'lending-account-' +
                        accounts.map((account) => account.id).join(','),
                  ),
                  initialValue: accounts.any((account) => account.id == accountId)
                      ? accountId
                      : null,
                  decoration: const InputDecoration(labelText: 'Account'),
                  items: accounts
                      .map(
                        (a) =>
                            DropdownMenuItem(value: a.id, child: Text(a.name)),
                      )
                      .toList(),
                  onChanged: saving
                      ? null
                      : (v) => setSheet(() => accountId = v ?? accountId),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: note,
                  enabled: !saving,
                  decoration: const InputDecoration(
                    labelText: 'Note (optional)',
                  ),
                ),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    due == null
                        ? 'Due date (optional)'
                        : 'Due date: ' +
                              due!.day.toString() +
                              '/' +
                              due!.month.toString() +
                              '/' +
                              due!.year.toString(),
                  ),
                  leading: const Icon(Icons.event_outlined),
                  onTap: saving
                      ? null
                      : () async {
                          final d = await showDatePicker(
                            context: sheet,
                            firstDate: DateTime(2020),
                            lastDate: DateTime(2100),
                            initialDate: due ?? DateTime.now(),
                          );
                          if (d != null) setSheet(() => due = d);
                        },
                ),
                FilledButton.icon(
                  onPressed: saving
                      ? null
                      : () async {
                          final p = person.text.trim(),
                              a = double.tryParse(amount.text);
                          if (p.isEmpty || a == null || a <= 0) {
                            ScaffoldMessenger.of(sheet).showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Enter a person and valid amount.',
                                ),
                              ),
                            );
                            return;
                          }
                          setSheet(() => saving = true);
                          try {
                            final created = await api.create(
                              widget.accessToken,
                              direction: direction,
                              accountId: accountId,
                              personName: p,
                              amount: a,
                              description: note.text,
                              dueDate: due,
                            );
                            if (sheet.mounted) Navigator.pop(sheet, created);
                          } catch (e) {
                            if (sheet.mounted) setSheet(() => saving = false);
                            ScaffoldMessenger.of(sheet).showSnackBar(
                              SnackBar(
                                content: Text(
                                  e is AppException
                                      ? e.message
                                      : 'Unable to save.',
                                ),
                              ),
                            );
                          }
                        },
                  icon: saving
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.check),
                  label: Text(
                    saving
                        ? 'Saving...'
                        : direction == 'LENT'
                        ? 'Save lent money'
                        : 'Save borrowed money',
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
    person.dispose();
    amount.dispose();
    note.dispose();
    if (saved != null && mounted) {
      setState(() {
        items = [saved, ...items.where((item) => item.id != saved.id)];
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lending record added successfully.')),
      );
      await load();
    }
    if (mounted) setState(() => _operationInProgress = false);
  }

  Future<void> repayRecord(LendingItem item) async {
    if (_operationInProgress || accounts.isEmpty) return;
    setState(() => _operationInProgress = true);
    final amount = TextEditingController(
          text: item.outstandingAmount.toStringAsFixed(2),
        ),
        note = TextEditingController();
    int accountId = accounts.first.id;
    DateTime date = DateTime.now();
    var saving = false;
    final saved = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheet) => StatefulBuilder(
        builder: (sheet, setSheet) => Padding(
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
                item.direction == 'LENT'
                    ? 'Record money received'
                    : 'Record repayment',
                style: Theme.of(sheet).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text('Outstanding ' + money(item.outstandingAmount)),
              const SizedBox(height: 8),
              TextField(
                controller: amount,
                enabled: !saving,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'Amount',
                  prefixText: '₹ ',
                ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<int>(
                key: ValueKey(
                  'lending-repay-account-' +
                      accounts.map((account) => account.id).join(','),
                ),
                initialValue: accounts.any((account) => account.id == accountId)
                    ? accountId
                    : null,
                decoration: const InputDecoration(labelText: 'Account'),
                items: accounts
                    .map(
                      (a) => DropdownMenuItem(value: a.id, child: Text(a.name)),
                    )
                    .toList(),
                onChanged: saving
                    ? null
                    : (v) => setSheet(() => accountId = v ?? accountId),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: note,
                enabled: !saving,
                decoration: const InputDecoration(labelText: 'Note (optional)'),
              ),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(
                  'Date: ' +
                      date.day.toString() +
                      '/' +
                      date.month.toString() +
                      '/' +
                      date.year.toString(),
                ),
                leading: const Icon(Icons.event_outlined),
                onTap: saving
                    ? null
                    : () async {
                        final d = await showDatePicker(
                          context: sheet,
                          firstDate: DateTime(2020),
                          lastDate: DateTime(2100),
                          initialDate: date,
                        );
                        if (d != null) setSheet(() => date = d);
                      },
              ),
              FilledButton.icon(
                onPressed: saving
                    ? null
                    : () async {
                        final a = double.tryParse(amount.text);
                        if (a == null || a <= 0 || a > item.outstandingAmount) {
                          ScaffoldMessenger.of(sheet).showSnackBar(
                            const SnackBar(
                              content: Text(
                                'Enter an amount within outstanding balance.',
                              ),
                            ),
                          );
                          return;
                        }
                        setSheet(() => saving = true);
                        try {
                          await api.repay(
                            widget.accessToken,
                            debtId: item.id,
                            accountId: accountId,
                            amount: a,
                            date: date,
                            note: note.text,
                          );
                          if (sheet.mounted) Navigator.pop(sheet, true);
                        } catch (e) {
                          if (sheet.mounted) setSheet(() => saving = false);
                          ScaffoldMessenger.of(sheet).showSnackBar(
                            SnackBar(
                              content: Text(
                                e is AppException
                                    ? e.message
                                    : 'Unable to record repayment.',
                              ),
                            ),
                          );
                        }
                      },
                icon: saving
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.check),
                label: Text(
                  saving
                      ? 'Saving...'
                      : item.direction == 'LENT'
                      ? 'Record received'
                      : 'Record repayment',
                ),
              ),
            ],
          ),
        ),
      ),
    );
    amount.dispose();
    note.dispose();
    if (saved == true) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Repayment recorded successfully.')),
        );
      }
      await load();
    }
    if (mounted) setState(() => _operationInProgress = false);
  }

  Future<void> cancelRecord(LendingItem item) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Cancel record?'),
        content: Text('Cancel the record for ' + item.personName + '?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Keep'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Cancel record'),
          ),
        ],
      ),
    );
    if (ok == true) {
      try {
        await api.cancel(widget.accessToken, item.id);
        await load();
      } catch (e) {
        if (mounted)
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                e is AppException ? e.message : 'Unable to cancel.',
              ),
            ),
          );
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: RefreshIndicator(
      onRefresh: load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 100),
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Lending',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 4),
                    const Text('Money you lent and money you borrowed'),
                  ],
                ),
              ),
              PopupMenuButton<String>(
                onSelected: _operationInProgress ? null : (v) => addRecord(v),
                itemBuilder: (_) => const [
                  PopupMenuItem(value: 'LENT', child: Text('Lend money')),
                  PopupMenuItem(value: 'BORROWED', child: Text('Borrow money')),
                ],
              ),
            ],
          ),
          const SizedBox(height: 14),
          if (summary != null)
            Row(
              children: [
                Expanded(
                  child: _summary(
                    'You lent',
                    summary!.lent,
                    summary!.lentCount,
                    Icons.arrow_upward,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _summary(
                    'You borrowed',
                    summary!.borrowed,
                    summary!.borrowedCount,
                    Icons.arrow_downward,
                  ),
                ),
              ],
            ),
          const SizedBox(height: 14),
          Row(
            children: [
              ChoiceChip(
                label: const Text('All'),
                selected: filter == 0,
                onSelected: (_) => setState(() => filter = 0),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: const Text('Lent'),
                selected: filter == 1,
                onSelected: (_) => setState(() => filter = 1),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: const Text('Borrowed'),
                selected: filter == 2,
                onSelected: (_) => setState(() => filter = 2),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (loading && items.isEmpty)
            const Center(child: CircularProgressIndicator())
          else if (error != null && items.isEmpty)
            Card(
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
            )
          else if (visible.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(Icons.handshake_outlined, size: 48),
                    SizedBox(height: 10),
                    Text('No lending records'),
                    SizedBox(height: 6),
                    Text(
                      'Track money lent to or borrowed from people.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            )
          else
            ...visible.map((x) => _item(context, x)),
        ],
      ),
    ),
  );
  Widget _summary(String title, double amount, int count, IconData icon) =>
      Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon),
              const SizedBox(height: 6),
              Text(title),
              Text(
                money(amount),
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              Text(count.toString() + ' active'),
            ],
          ),
        ),
      );
  Widget _item(BuildContext context, LendingItem item) => Card(
    child: Padding(
      padding: const EdgeInsets.all(15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                item.direction == 'LENT'
                    ? Icons.arrow_upward
                    : Icons.arrow_downward,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  item.personName,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
              if (item.status != 'SETTLED' && item.status != 'CANCELLED')
                PopupMenuButton<String>(
                  onSelected: (v) {
                    if (v == 'repay') repayRecord(item);
                    if (v == 'cancel') cancelRecord(item);
                  },
                  itemBuilder: (_) => const [
                    PopupMenuItem(
                      value: 'repay',
                      child: Text('Record repayment'),
                    ),
                    PopupMenuItem(value: 'cancel', child: Text('Cancel')),
                  ],
                ),
            ],
          ),
          if (item.description != null && item.description!.isNotEmpty)
            Text(item.description!),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _metric('Original', money(item.originalAmount))),
              Expanded(
                child: _metric('Outstanding', money(item.outstandingAmount)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text('Status: ' + item.status.replaceAll('_', ' ')),
          if (item.dueDate != null)
            Text(
              'Due: ' +
                  item.dueDate!.day.toString() +
                  '/' +
                  item.dueDate!.month.toString() +
                  '/' +
                  item.dueDate!.year.toString(),
            ),
        ],
      ),
    ),
  );
  Widget _metric(String label, String value) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(label),
      Text(
        value,
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    ],
  );
}
