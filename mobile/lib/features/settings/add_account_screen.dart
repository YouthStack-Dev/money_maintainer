import 'package:flutter/material.dart';
import 'finance_service.dart';

class AddAccountScreen extends StatefulWidget {
  const AddAccountScreen({super.key});
  @override
  State<AddAccountScreen> createState() => _AddAccountScreenState();
}

class _AddAccountScreenState extends State<AddAccountScreen> {
  final _form = GlobalKey<FormState>();
  final _name = TextEditingController(),
      _institution = TextEditingController(),
      _balance = TextEditingController(text: '0');
  String _type = 'CASH';
  bool _saving = false;
  static const types = {
    'CASH': 'Cash',
    'BANK_ACCOUNT': 'Bank account',
    'CREDIT_CARD': 'Credit card',
    'WALLET': 'Wallet'
  };
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
      await FinanceService().createAccount(
          name: _name.text,
          type: _type,
          openingBalance: double.parse(_balance.text),
          institution: _institution.text);
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
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(title: const Text('Add account')),
      body: Form(
          key: _form,
          child: ListView(padding: const EdgeInsets.all(20), children: [
            const Text('Add where you keep money',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            const Text('Cash, bank account, credit card or wallet.'),
            const SizedBox(height: 24),
            TextFormField(
                controller: _name,
                decoration: const InputDecoration(
                    labelText: 'Account name', hintText: 'e.g. HDFC Salary'),
                validator: (v) => v == null || v.trim().isEmpty
                    ? 'Enter an account name'
                    : null),
            const SizedBox(height: 14),
            DropdownButtonFormField<String>(
                initialValue: _type,
                decoration: const InputDecoration(labelText: 'Account type'),
                items: types.entries
                    .map((e) =>
                        DropdownMenuItem(value: e.key, child: Text(e.value)))
                    .toList(),
                onChanged: (v) {
                  if (v != null) setState(() => _type = v);
                }),
            const SizedBox(height: 14),
            TextFormField(
                controller: _institution,
                decoration: const InputDecoration(
                    labelText: 'Bank / institution (optional)')),
            const SizedBox(height: 14),
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
            FilledButton.icon(
                onPressed: _saving ? null : _save,
                icon: const Icon(Icons.add),
                label: Text(_saving ? 'Creating...' : 'Create account')),
          ])));
}
