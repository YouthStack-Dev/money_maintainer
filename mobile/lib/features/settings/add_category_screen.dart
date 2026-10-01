import 'package:flutter/material.dart';
import 'finance_service.dart';

class AddCategoryScreen extends StatefulWidget {
  const AddCategoryScreen(
      {super.key, this.type = 'EXPENSE', this.parents = const []});
  final String type;
  final List<FinanceCategory> parents;
  @override
  State<AddCategoryScreen> createState() => _AddCategoryScreenState();
}

class _AddCategoryScreenState extends State<AddCategoryScreen> {
  final _form = GlobalKey<FormState>();
  final _name = TextEditingController();
  int? _parent;
  bool _saving = false;
  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      await FinanceService().createCategory(
          name: _name.text, type: widget.type, parentId: _parent);
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
      appBar: AppBar(
          title: Text(widget.type == 'EXPENSE'
              ? 'Add expense category'
              : 'Add income category')),
      body: Form(
          key: _form,
          child: ListView(padding: const EdgeInsets.all(20), children: [
            Text(
                widget.type == 'EXPENSE'
                    ? 'What do you spend money on?'
                    : 'Where does your income come from?',
                style:
                    const TextStyle(fontSize: 22, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            const Text('Categories make your reports easier to understand.'),
            const SizedBox(height: 24),
            TextFormField(
                controller: _name,
                autofocus: true,
                decoration: const InputDecoration(
                    labelText: 'Category name',
                    hintText: 'e.g. Food, Rent, Salary'),
                validator: (v) => v == null || v.trim().isEmpty
                    ? 'Enter a category name'
                    : null),
            if (widget.parents.isNotEmpty) ...[
              const SizedBox(height: 14),
              DropdownButtonFormField<int>(
                  initialValue: _parent,
                  decoration: const InputDecoration(
                      labelText: 'Parent category (optional)'),
                  items: widget.parents
                      .map((p) =>
                          DropdownMenuItem(value: p.id, child: Text(p.name)))
                      .toList(),
                  onChanged: (v) => setState(() => _parent = v))
            ],
            const SizedBox(height: 28),
            FilledButton.icon(
                onPressed: _saving ? null : _save,
                icon: const Icon(Icons.add),
                label: Text(_saving ? 'Creating...' : 'Create category')),
          ])));
}
