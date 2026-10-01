import 'package:flutter/material.dart';
import 'finance_service.dart';

class EditCategoryScreen extends StatefulWidget {
  const EditCategoryScreen(
      {super.key, required this.category, required this.allCategories});
  final FinanceCategory category;
  final List<FinanceCategory> allCategories;
  @override
  State<EditCategoryScreen> createState() => _EditCategoryScreenState();
}

class _EditCategoryScreenState extends State<EditCategoryScreen> {
  final _form = GlobalKey<FormState>();
  late final TextEditingController _name;
  late String _type;
  late int? _parent;
  bool _saving = false;
  @override
  void initState() {
    super.initState();
    _name = TextEditingController(text: widget.category.name);
    _type = widget.category.type;
    _parent = widget.category.parentId;
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  List<FinanceCategory> get _parents => widget.allCategories
      .where((c) => c.id != widget.category.id && c.type == _type && c.isActive)
      .toList();
  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final updated = await FinanceService().updateCategory(widget.category.id,
          name: _name.text, type: _type, parentId: _parent, setParent: true);
      if (mounted) Navigator.pop(context, updated);
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
        appBar: AppBar(title: const Text('Edit category')),
        body: Form(
            key: _form,
            child: ListView(padding: const EdgeInsets.all(20), children: [
              TextFormField(
                  controller: _name,
                  decoration: const InputDecoration(labelText: 'Category name'),
                  validator: (v) => v == null || v.trim().isEmpty
                      ? 'Enter a category name'
                      : null),
              const SizedBox(height: 14),
              DropdownButtonFormField<String>(
                  initialValue: _type,
                  decoration: const InputDecoration(labelText: 'Category type'),
                  items: const [
                    DropdownMenuItem(value: 'EXPENSE', child: Text('Expense')),
                    DropdownMenuItem(value: 'INCOME', child: Text('Income'))
                  ],
                  onChanged: (v) => setState(() {
                        _type = v!;
                        if (!_parents.any((p) => p.id == _parent))
                          _parent = null;
                      })),
              const SizedBox(height: 14),
              DropdownButtonFormField<int?>(
                  initialValue: _parent,
                  decoration: const InputDecoration(
                      labelText: 'Parent category (optional)'),
                  items: [
                    const DropdownMenuItem<int?>(
                        value: null, child: Text('No parent')),
                    ..._parents.map((p) => DropdownMenuItem<int?>(
                        value: p.id, child: Text(p.name)))
                  ],
                  onChanged: (v) => setState(() => _parent = v)),
              const SizedBox(height: 28),
              FilledButton.icon(
                  onPressed: _saving ? null : _save,
                  icon: const Icon(Icons.save_outlined),
                  label: Text(_saving ? 'Saving...' : 'Save changes')),
            ])),
      );
}
