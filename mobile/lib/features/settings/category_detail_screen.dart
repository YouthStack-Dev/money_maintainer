import 'package:flutter/material.dart';
import 'finance_service.dart';
import 'edit_category_screen.dart';

class CategoryDetailScreen extends StatefulWidget {
  const CategoryDetailScreen(
      {super.key, required this.category, required this.allCategories});
  final FinanceCategory category;
  final List<FinanceCategory> allCategories;
  @override
  State<CategoryDetailScreen> createState() => _CategoryDetailScreenState();
}

class _CategoryDetailScreenState extends State<CategoryDetailScreen> {
  final _service = FinanceService();
  late FinanceCategory _category;
  bool _loading = false;
  @override
  void initState() {
    super.initState();
    _category = widget.category;
  }

  FinanceCategory? get _parent {
    if (_category.parentId == null) return null;
    for (final c in widget.allCategories) {
      if (c.id == _category.parentId) return c;
    }
    return null;
  }

  Future<void> _edit() async {
    final result = await Navigator.push(
        context,
        MaterialPageRoute(
            builder: (_) => EditCategoryScreen(
                category: _category, allCategories: widget.allCategories)));
    if (result is FinanceCategory && mounted)
      setState(() => _category = result);
  }

  Future<void> _delete() async {
    final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
              title: const Text('Delete category?'),
              content: const Text(
                  'This will deactivate the category. Existing transaction history is kept safe.'),
              actions: [
                TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: const Text('Cancel')),
                FilledButton(
                    onPressed: () => Navigator.pop(context, true),
                    child: const Text('Delete')),
              ],
            ));
    if (confirmed != true) return;
    setState(() => _loading = true);
    try {
      await _service.deleteCategory(_category.id);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final parent = _parent;
    return Scaffold(
      appBar: AppBar(title: const Text('Category details')),
      body: ListView(padding: const EdgeInsets.all(20), children: [
        CircleAvatar(
            radius: 30,
            child: Icon(_category.type == 'EXPENSE'
                ? Icons.arrow_upward
                : Icons.arrow_downward)),
        const SizedBox(height: 16),
        Center(
            child: Text(_category.name,
                style: Theme.of(context).textTheme.headlineSmall)),
        const SizedBox(height: 24),
        _row('Type', _category.type == 'EXPENSE' ? 'Expense' : 'Income'),
        _row('Parent', parent?.name ?? 'None'),
        _row('Status', _category.isActive ? 'Active' : 'Inactive'),
        _row('ID', _category.id.toString()),
        const SizedBox(height: 28),
        FilledButton.icon(
            onPressed: _loading || !_category.isActive ? null : _edit,
            icon: const Icon(Icons.edit),
            label: const Text('Edit category')),
        const SizedBox(height: 10),
        OutlinedButton.icon(
            onPressed: _loading || !_category.isActive ? null : _delete,
            icon: const Icon(Icons.delete_outline),
            label: Text(_loading ? 'Deleting...' : 'Delete category')),
      ]),
    );
  }

  Widget _row(String label, String value) => Padding(
      padding: const EdgeInsets.symmetric(vertical: 9),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        SizedBox(
            width: 100,
            child: Text(label,
                style: const TextStyle(fontWeight: FontWeight.w600))),
        Expanded(child: Text(value)),
      ]));
}
