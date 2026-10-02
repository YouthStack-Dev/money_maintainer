// ignore_for_file: prefer_interpolation_to_compose_strings, use_build_context_synchronously
import 'package:flutter/material.dart';

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../data/money_api.dart';

class MoneyPage extends StatefulWidget {
  const MoneyPage({required this.accessToken, super.key});

  final String accessToken;

  @override
  State<MoneyPage> createState() => _MoneyPageState();
}

class _MoneyPageState extends State<MoneyPage> {
  late final MoneyApi api;
  List<MoneyTransaction> transactions = [];
  List<MoneyAccount> accounts = [];
  List<MoneyCategory> categories = [];
  bool loading = true;
  bool _operationInProgress = false;
  String? error;

  @override
  void initState() {
    super.initState();
    api = MoneyApi(config: AppEnvironmentConfig.development);
    load();
  }

  Future<void> load() async {
    if (!mounted) return;
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final result = await Future.wait([
        api.list(widget.accessToken),
        api.accounts(widget.accessToken),
        api.categories(widget.accessToken),
      ]);

      if (!mounted) return;
      setState(() {
        transactions = result[0] as List<MoneyTransaction>;
        accounts = result[1] as List<MoneyAccount>;
        categories = result[2] as List<MoneyCategory>;
      });
    } catch (e) {
      if (mounted) {
        setState(
          () => error = e is AppException ? e.message : 'Unable to load money.',
        );
      }
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  void msg(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  void success(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> openForm([MoneyTransaction? old]) async {
    if (_operationInProgress) return;
    setState(() => _operationInProgress = true);
    try {
      final saved = await form(old);
      if (saved == null || !mounted) return;

    setState(() {
      if (old == null) {
        transactions = [
          saved,
          ...transactions.where((item) => item.id != saved.id),
        ];
      } else {
        transactions = transactions
            .map((item) => item.id == saved.id ? saved : item)
            .toList();
      }
    });

    success(
      old == null
          ? 'Money entry added successfully.'
          : 'Money entry updated successfully.',
    );

    // Reconcile the local result with the server. If the refresh fails,
    // the just-created/updated entry remains visible instead of disappearing.
    await load();
    } finally {
      if (mounted) setState(() => _operationInProgress = false);
    }
  }

  Future<MoneyTransaction?> form([MoneyTransaction? old]) async {
    final uniqueAccounts = _uniqueAccounts(accounts);
    if (uniqueAccounts.isEmpty) {
      msg('Add an active account first.');
      return null;
    }

    final amount = TextEditingController(
      text: old == null ? '' : old.amount.toStringAsFixed(2),
    );
    final description = TextEditingController(text: old?.description ?? '');

    var type = old?.type ?? 'EXPENSE';
    var account = uniqueAccounts.any((item) => item.id == old?.accountId)
        ? old!.accountId
        : uniqueAccounts.first.id;
    var category = old?.categoryId;
    var destination = old?.transferAccountId;
    var date = old?.date ?? DateTime.now();
    var saving = false;

    final result = await showModalBottomSheet<MoneyTransaction?>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheet) => StatefulBuilder(
        builder: (sheet, setSheet) {
          final categoryItems = _uniqueCategories(
            categories.where((item) {
              return item.type == type ||
                  (type == 'REFUND' && item.type == 'INCOME');
            }).toList(),
          );

          if (!categoryItems.any((item) => item.id == category)) {
            category = null;
          }

          final destinationItems = uniqueAccounts
              .where((item) => item.id != account)
              .toList();

          if (!destinationItems.any((item) => item.id == destination)) {
            destination = null;
          }

          Future<void> submit() async {
            if (saving) return;

            final value = double.tryParse(amount.text.trim());
            if (value == null || value <= 0) {
              ScaffoldMessenger.of(sheet).showSnackBar(
                const SnackBar(content: Text('Enter a valid amount.')),
              );
              return;
            }

            if (type == 'TRANSFER' &&
                (destination == null || destination == account)) {
              ScaffoldMessenger.of(sheet).showSnackBar(
                const SnackBar(
                  content: Text('Choose a different destination account.'),
                ),
              );
              return;
            }

            setSheet(() => saving = true);

            try {
              final categoryId = type == 'TRANSFER' ? null : category;
              final transferId = type == 'TRANSFER' ? destination : null;

              final saved = old == null
                  ? await api.create(
                      widget.accessToken,
                      accountId: account,
                      categoryId: categoryId,
                      transferAccountId: transferId,
                      type: type,
                      amount: value,
                      description: description.text.trim().isEmpty
                          ? null
                          : description.text.trim(),
                      date: date,
                    )
                  : await api.update(
                      widget.accessToken,
                      old.id,
                      accountId: account,
                      categoryId: categoryId,
                      transferAccountId: transferId,
                      type: type,
                      amount: value,
                      description: description.text.trim().isEmpty
                          ? null
                          : description.text.trim(),
                      date: date,
                    );

              if (sheet.mounted) {
                Navigator.pop(sheet, saved);
              }
            } catch (e) {
              if (sheet.mounted) {
                setSheet(() => saving = false);
                ScaffoldMessenger.of(sheet).showSnackBar(
                  SnackBar(
                    content: Text(
                      e is AppException ? e.message : 'Unable to save entry.',
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
                10,
                20,
                MediaQuery.viewInsetsOf(sheet).bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      old == null ? 'Add money entry' : 'Edit money entry',
                      style: Theme.of(sheet).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 12),
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'EXPENSE', label: Text('Expense')),
                        ButtonSegment(value: 'INCOME', label: Text('Income')),
                        ButtonSegment(value: 'REFUND', label: Text('Refund')),
                        ButtonSegment(
                          value: 'TRANSFER',
                          label: Text('Transfer'),
                        ),
                      ],
                      selected: {type},
                      onSelectionChanged: saving
                          ? null
                          : (value) {
                              setSheet(() {
                                type = value.first;
                                category = null;
                                destination = null;
                              });
                            },
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<int>(
                      initialValue: account,
                      decoration: const InputDecoration(labelText: 'Account'),
                      items: uniqueAccounts
                          .map(
                            (item) => DropdownMenuItem(
                              value: item.id,
                              child: Text(item.name),
                            ),
                          )
                          .toList(),
                      onChanged: saving
                          ? null
                          : (value) {
                              if (value == null) return;
                              setSheet(() {
                                account = value;
                                if (destination == account) {
                                  destination = null;
                                }
                              });
                            },
                    ),
                    if (type == 'TRANSFER') ...[
                      const SizedBox(height: 10),
                      DropdownButtonFormField<int>(
                        initialValue: destination,
                        decoration: const InputDecoration(
                          labelText: 'To account',
                        ),
                        items: destinationItems
                            .map(
                              (item) => DropdownMenuItem(
                                value: item.id,
                                child: Text(item.name),
                              ),
                            )
                            .toList(),
                        onChanged: saving
                            ? null
                            : (value) => setSheet(() => destination = value),
                      ),
                    ] else ...[
                      const SizedBox(height: 10),
                      DropdownButtonFormField<int>(
                        initialValue: category,
                        decoration: const InputDecoration(
                          labelText: 'Category (optional)',
                        ),
                        items: categoryItems
                            .map(
                              (item) => DropdownMenuItem(
                                value: item.id,
                                child: Text(item.name),
                              ),
                            )
                            .toList(),
                        onChanged: saving
                            ? null
                            : (value) => setSheet(() => category = value),
                      ),
                    ],
                    const SizedBox(height: 10),
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
                    const SizedBox(height: 10),
                    TextField(
                      controller: description,
                      enabled: !saving,
                      decoration: const InputDecoration(
                        labelText: 'Description',
                      ),
                      maxLines: 2,
                    ),
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Date'),
                      subtitle: Text(_date(date)),
                      trailing: const Icon(Icons.calendar_today),
                      onTap: saving
                          ? null
                          : () async {
                              final picked = await showDatePicker(
                                context: sheet,
                                initialDate: date,
                                firstDate: DateTime(2020),
                                lastDate: DateTime(2100),
                              );
                              if (picked != null) {
                                setSheet(
                                  () => date = DateTime(
                                    picked.year,
                                    picked.month,
                                    picked.day,
                                    date.hour,
                                    date.minute,
                                  ),
                                );
                              }
                            },
                    ),
                    const SizedBox(height: 8),
                    FilledButton.icon(
                      onPressed: saving ? null : submit,
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
                            : old == null
                            ? 'Add entry'
                            : 'Save changes',
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );

    amount.dispose();
    description.dispose();
    return result;
  }

  Future<void> remove(MoneyTransaction transaction) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (dialog) => AlertDialog(
        title: const Text('Remove entry?'),
        content: const Text('This transaction will be deactivated.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialog, false),
            child: const Text('Keep'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialog, true),
            child: const Text('Remove'),
          ),
        ],
      ),
    );

    if (ok != true) return;

    try {
      await api.remove(widget.accessToken, transaction.id);
      if (mounted) {
        setState(
          () => transactions = transactions
              .where((item) => item.id != transaction.id)
              .toList(),
        );
      }
      success('Money entry removed.');
      await load();
    } catch (e) {
      msg(e is AppException ? e.message : 'Unable to remove entry.');
    }
  }

  List<MoneyAccount> _uniqueAccounts(List<MoneyAccount> source) {
    final seen = <int>{};
    return source.where((item) => seen.add(item.id)).toList();
  }

  List<MoneyCategory> _uniqueCategories(List<MoneyCategory> source) {
    final seen = <int>{};
    return source.where((item) => seen.add(item.id)).toList();
  }

  String _date(DateTime value) =>
      value.day.toString().padLeft(2, '0') +
      '/' +
      value.month.toString().padLeft(2, '0') +
      '/' +
      value.year.toString();

  @override
  Widget build(BuildContext context) => Scaffold(
    body: RefreshIndicator(
      onRefresh: load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 100),
        children: [
          Text('Money', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 6),
          const Text('Income, expenses, refunds and transfers'),
          const SizedBox(height: 16),
          if (loading && transactions.isEmpty)
            const Center(child: CircularProgressIndicator())
          else if (error != null && transactions.isEmpty)
            _errorState()
          else if (transactions.isEmpty)
            _empty()
          else
            ...transactions.map(_tile),
        ],
      ),
    ),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: loading || _operationInProgress ? null : openForm,
      icon: const Icon(Icons.add),
      label: const Text('Add entry'),
    ),
  );

  Widget _errorState() => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const Icon(Icons.cloud_off_outlined, size: 44),
          const SizedBox(height: 10),
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

  Widget _empty() => Card(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const Icon(Icons.receipt_long_outlined, size: 48),
          const SizedBox(height: 10),
          Text(
            'No money entries yet',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          const Text(
            'Record your first expense or income.',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _operationInProgress ? null : openForm,
            icon: const Icon(Icons.add),
            label: const Text('Add entry'),
          ),
        ],
      ),
    ),
  );

  Widget _tile(MoneyTransaction transaction) {
    final incoming =
        transaction.type == 'INCOME' || transaction.type == 'REFUND';
    final account =
        accounts
            .where((item) => item.id == transaction.accountId)
            .firstOrNull
            ?.name ??
        'Account';

    return Card(
      child: ListTile(
        leading: CircleAvatar(
          child: Icon(
            transaction.type == 'TRANSFER'
                ? Icons.swap_horiz
                : incoming
                ? Icons.arrow_downward
                : Icons.arrow_upward,
          ),
        ),
        title: Text(
          transaction.description.isEmpty
              ? transaction.type
              : transaction.description,
        ),
        subtitle: Text(
          transaction.type + ' • ' + account + ' • ' + _date(transaction.date),
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            if (value == 'edit') {
              openForm(transaction);
            } else {
              remove(transaction);
            }
          },
          itemBuilder: (_) => const [
            PopupMenuItem(value: 'edit', child: Text('Edit')),
            PopupMenuItem(value: 'remove', child: Text('Remove')),
          ],
        ),
      ),
    );
  }
}
