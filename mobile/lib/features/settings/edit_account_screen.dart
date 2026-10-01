import 'package:flutter/material.dart';
import 'finance_service.dart';

class EditAccountScreen extends StatefulWidget {
  const EditAccountScreen({super.key, required this.account});
  final FinanceAccount account;
  @override
  State<EditAccountScreen> createState() => _EditAccountScreenState();
}

class _EditAccountScreenState extends State<EditAccountScreen> {
  final _form = GlobalKey<FormState>();
  late final TextEditingController _name, _institution, _balance;
  bool _saving = false;
  @override
  void initState() {
    super.initState();
    _name = TextEditingController(text: widget.account.name);
    _institution =
        TextEditingController(text: widget.account.institution ?? '');
    _balance =
        TextEditingController(text: widget.account.balance.toStringAsFixed(2));
  }

  @override
  void dispose() {
    _name.dispose();
    _institution.dispose();
    _balance.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      await FinanceService().updateAccount(widget.account.id,
          name: _name.text,
          institution: _institution.text,
          openingBalance: double.parse(_balance.text));
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Edit account')),
      body: Form(
        key: _form,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            TextFormField(
                controller: _name,
                decoration: const InputDecoration(labelText: 'Account name'),
                validator: (v) => v == null || v.trim().isEmpty
                    ? 'Enter an account name'
                    : null),
            const SizedBox(height: 16),
            Text(
                'Type: ${widget.account.type == 'BANK_ACCOUNT' ? 'Bank account' : widget.account.type == 'CREDIT_CARD' ? 'Credit card' : widget.account.type == 'WALLET' ? 'Wallet' : 'Cash'}'),
            const SizedBox(height: 16),
            TextFormField(
                controller: _institution,
                decoration: const InputDecoration(
                    labelText: 'Bank / institution (optional)')),
            const SizedBox(height: 16),
            TextFormField(
                controller: _balance,
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                    labelText: 'Opening balance', prefixText: '₹ '),
                validator: (v) => double.tryParse(v ?? '') == null
                    ? 'Enter a valid amount'
                    : null),
            const SizedBox(height: 28),
            FilledButton(
                onPressed: _saving ? null : _save,
                child: Text(_saving ? 'Saving...' : 'Save changes')),
          ],
        ),
      ),
    );
  }
}
