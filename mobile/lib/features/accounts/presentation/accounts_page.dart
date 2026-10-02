// ignore_for_file: prefer_interpolation_to_compose_strings, use_build_context_synchronously
import 'package:flutter/material.dart';

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../data/accounts_api.dart';

class AccountsPage extends StatefulWidget {
  const AccountsPage({required this.accessToken, super.key});

  final String accessToken;

  @override
  State<AccountsPage> createState() => _AccountsPageState();
}

class _AccountsPageState extends State<AccountsPage> {
  late final AccountsApi api;
  List<AccountItem> items = [];
  bool loading = true;
  bool _operationInProgress = false;
  String? error;

  @override
  void initState() {
    super.initState();
    api = AccountsApi(config: AppEnvironmentConfig.development);
    load();
  }

  Future<void> load() async {
    if (!mounted) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final value = await api.list(widget.accessToken);
      if (mounted) {
        setState(() {
          items = value.where((a) => a.active).toList();
        });
      }
    } catch (e) {
      if (mounted) {
        setState(
          () => error = e is AppException
              ? e.message
              : 'Unable to load accounts.',
        );
      }
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> add() async {
    if (_operationInProgress) return;
    setState(() => _operationInProgress = true);
    try {
      final result = await form();
      if (result == null) return;

      final created = await api.create(
        widget.accessToken,
        result.name,
        result.type,
        result.institution,
        result.balance,
      );

      if (!mounted) return;
      setState(() {
        items = [...items.where((item) => item.id != created.id), created];
        error = null;
      });
      _success('Account "' + created.name + '" added successfully.');
      await load();
    } catch (e) {
      msg(e);
    } finally {
      if (mounted) setState(() => _operationInProgress = false);
    }
  }

  Future<void> edit(AccountItem account) async {
    if (_operationInProgress) return;
    setState(() => _operationInProgress = true);
    try {
      final result = await form(account);
      if (result == null) return;

      final updated = await api.update(
        widget.accessToken,
        account.id,
        result.name,
        result.institution,
        result.balance,
      );

      if (!mounted) return;
      setState(() {
        items = items
            .map((item) => item.id == updated.id ? updated : item)
            .toList();
      });
      _success('Account updated successfully.');
      await load();
    } catch (e) {
      msg(e);
    } finally {
      if (mounted) setState(() => _operationInProgress = false);
    }
  }

  Future<void> remove(AccountItem account) async {
    if (_operationInProgress) return;
    setState(() => _operationInProgress = true);
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Remove account?'),
        content: Text(account.name + ' will be deactivated.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Keep'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Remove'),
          ),
        ],
      ),
    );
    if (ok != true) {
      if (mounted) setState(() => _operationInProgress = false);
      return;
    }

    try {
      await api.remove(widget.accessToken, account.id);
      if (!mounted) return;
      setState(() {
        items = items.where((item) => item.id != account.id).toList();
      });
      _success('Account removed.');
      await load();
    } catch (e) {
      msg(e);
    } finally {
      if (mounted) setState(() => _operationInProgress = false);
    }
  }

  void msg(Object errorObject) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          errorObject is AppException
              ? errorObject.message
              : 'Request failed. Please try again.',
        ),
      ),
    );
  }

  void _success(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<_AccountForm?> form([AccountItem? account]) async {
    final nameController = TextEditingController(text: account?.name ?? '');
    final institutionController = TextEditingController(
      text: account?.institution ?? '',
    );
    final balanceController = TextEditingController(
      text: account == null ? '' : account.balance.toStringAsFixed(2),
    );

    var type = account?.type ?? 'BANK_ACCOUNT';
    var saving = false;

    final result = await showModalBottomSheet<_AccountForm>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      isDismissible: true,
      builder: (sheetContext) => StatefulBuilder(
        builder: (sheetContext, setSheetState) {
          Future<void> submit() async {
            if (saving) return;

            final name = nameController.text.trim();
            final balance = double.tryParse(balanceController.text.trim()) ?? 0;

            if (name.isEmpty) {
              ScaffoldMessenger.of(sheetContext).showSnackBar(
                const SnackBar(content: Text('Enter an account name.')),
              );
              return;
            }
            if (balance < 0 && type == 'CASH') {
              ScaffoldMessenger.of(sheetContext).showSnackBar(
                const SnackBar(
                  content: Text('Cash opening balance cannot be negative.'),
                ),
              );
              return;
            }

            setSheetState(() => saving = true);

            // The actual API request is owned by the parent page. Returning
            // the form closes this sheet exactly once after validation.
            if (sheetContext.mounted) {
              Navigator.pop(
                sheetContext,
                _AccountForm(
                  name,
                  type,
                  institutionController.text.trim(),
                  balance,
                ),
              );
            }
          }

          return PopScope(
            canPop: !saving,
            child: Padding(
              padding: EdgeInsets.fromLTRB(
                20,
                10,
                20,
                MediaQuery.viewInsetsOf(sheetContext).bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      account == null ? 'Add account' : 'Edit account',
                      style: Theme.of(sheetContext).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: nameController,
                      enabled: !saving,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Account name',
                        prefixIcon: Icon(Icons.account_balance_wallet_outlined),
                      ),
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      initialValue: type,
                      decoration: const InputDecoration(
                        labelText: 'Account type',
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: 'BANK_ACCOUNT',
                          child: Text('Bank account'),
                        ),
                        DropdownMenuItem(value: 'CASH', child: Text('Cash')),
                        DropdownMenuItem(
                          value: 'WALLET',
                          child: Text('Wallet'),
                        ),
                        DropdownMenuItem(
                          value: 'CREDIT_CARD',
                          child: Text('Credit card'),
                        ),
                      ],
                      onChanged: account == null && !saving
                          ? (value) {
                              if (value != null) {
                                setSheetState(() => type = value);
                              }
                            }
                          : null,
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: institutionController,
                      enabled: !saving,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Institution / bank',
                      ),
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: balanceController,
                      enabled: !saving,
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                        signed: true,
                      ),
                      decoration: const InputDecoration(
                        labelText: 'Opening balance',
                        prefixText: '₹ ',
                      ),
                    ),
                    const SizedBox(height: 18),
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
                            : account == null
                            ? 'Create account'
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

    nameController.dispose();
    institutionController.dispose();
    balanceController.dispose();
    return result;
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
            Text('Accounts', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 6),
            const Text('Bank, cash, wallet and credit accounts'),
            const SizedBox(height: 16),
            if (loading && items.isEmpty)
              const Center(child: CircularProgressIndicator())
            else if (error != null && items.isEmpty)
              _errorState(context)
            else if (items.isEmpty)
              _empty(context)
            else
              ...items.map(_tile),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: loading || _operationInProgress ? null : add,
        icon: const Icon(Icons.add),
        label: const Text('Add account'),
      ),
    );
  }

  Widget _errorState(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const Icon(Icons.cloud_off_outlined, size: 44),
          const SizedBox(height: 10),
          Text(error!, textAlign: TextAlign.center),
          const SizedBox(height: 14),
          FilledButton.icon(
            onPressed: load,
            icon: const Icon(Icons.refresh),
            label: const Text('Retry'),
          ),
        ],
      ),
    ),
  );

  Widget _empty(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const Icon(Icons.account_balance_wallet_outlined, size: 48),
          const SizedBox(height: 10),
          Text(
            'No accounts yet',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 12),
          const Text(
            'Add your bank account, cash or wallet to start tracking money.',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _operationInProgress ? null : add,
            icon: const Icon(Icons.add),
            label: const Text('Add first account'),
          ),
        ],
      ),
    ),
  );

  Widget _tile(AccountItem account) => Card(
    child: ListTile(
      leading: CircleAvatar(child: Icon(_icon(account.type))),
      title: Text(account.name),
      subtitle: Text(
        account.type.replaceAll('_', ' ') +
            (account.institution?.isNotEmpty == true
                ? ' • ' + account.institution!
                : ''),
      ),
      trailing: PopupMenuButton<String>(
        onSelected: (value) =>
            value == 'edit' ? edit(account) : remove(account),
        itemBuilder: (_) => const [
          PopupMenuItem(value: 'edit', child: Text('Edit')),
          PopupMenuItem(value: 'remove', child: Text('Remove')),
        ],
      ),
    ),
  );

  IconData _icon(String type) => switch (type) {
    'BANK_ACCOUNT' => Icons.account_balance_outlined,
    'CASH' => Icons.payments_outlined,
    'CREDIT_CARD' => Icons.credit_card_outlined,
    _ => Icons.account_balance_wallet_outlined,
  };
}

class _AccountForm {
  const _AccountForm(this.name, this.type, this.institution, this.balance);

  final String name;
  final String type;
  final String institution;
  final double balance;
}
