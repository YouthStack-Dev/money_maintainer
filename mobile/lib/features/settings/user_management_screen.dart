import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'user_service.dart';

class UserManagementScreen extends StatefulWidget {
  const UserManagementScreen({super.key});
  @override
  State<UserManagementScreen> createState() => _UserManagementScreenState();
}

class _UserManagementScreenState extends State<UserManagementScreen> {
  final _service = UserService();
  late Future<List<ManagedUser>> _users;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _users = _service.list();

  Future<void> _refresh() async {
    setState(_load);
    await _users;
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Manage users')),
        floatingActionButton: FloatingActionButton.extended(
            onPressed: _create,
            icon: const Icon(Icons.person_add),
            label: const Text('Add user')),
        body: FutureBuilder<List<ManagedUser>>(
          future: _users,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done)
              return const Center(child: CircularProgressIndicator());
            if (snapshot.hasError)
              return _ErrorState(error: snapshot.error!, onRetry: _refresh);
            final users = snapshot.data!;
            if (users.isEmpty)
              return RefreshIndicator(
                  onRefresh: _refresh,
                  child: ListView(children: const [
                    SizedBox(height: 160),
                    Center(child: Text('No users found.'))
                  ]));
            return RefreshIndicator(
              onRefresh: _refresh,
              child: ListView.separated(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
                itemCount: users.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (_, index) {
                  final user = users[index];
                  final status = user.isActive ? 'Active' : 'Inactive';
                  final verification =
                      user.isEmailVerified ? 'Verified' : 'Unverified';
                  return Card(
                    child: ListTile(
                      onTap: () => _open(user.id),
                      leading: CircleAvatar(
                          child: Text(user.fullName.isEmpty
                              ? '?'
                              : user.fullName[0].toUpperCase())),
                      title: Text(user.fullName),
                      subtitle: Text(
                          user.email + '\n' + status + ' · ' + verification),
                      isThreeLine: true,
                      trailing: const Icon(Icons.chevron_right),
                    ),
                  );
                },
              ),
            );
          },
        ),
      );

  Future<void> _create() async {
    final result = await showDialog<bool>(
        context: context, builder: (_) => const _UserFormDialog());
    if (result == true && mounted) setState(_load);
  }

  Future<void> _open(int id) async {
    try {
      final user = await _service.get(id);
      if (!mounted) return;
      final changed = await Navigator.push<bool>(
          context,
          MaterialPageRoute(
              builder: (_) =>
                  _UserDetailScreen(user: user, service: _service)));
      if (changed == true && mounted) setState(_load);
    } catch (e) {
      if (mounted) _showError(e);
    }
  }

  void _showError(Object e) {
    final message = e is ApiException
        ? e.userMessage
        : 'Something went wrong. Please try again.';
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error, required this.onRetry});
  final Object error;
  final Future<void> Function() onRetry;

  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.error_outline, size: 42),
            const SizedBox(height: 12),
            Text(
                error is ApiException
                    ? (error as ApiException).userMessage
                    : 'Could not load users.',
                textAlign: TextAlign.center),
            const SizedBox(height: 12),
            FilledButton(onPressed: onRetry, child: const Text('Retry')),
          ]),
        ),
      );
}

class _UserFormDialog extends StatefulWidget {
  const _UserFormDialog();
  @override
  State<_UserFormDialog> createState() => _UserFormDialogState();
}

class _UserFormDialogState extends State<_UserFormDialog> {
  final _service = UserService();
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _name = TextEditingController();
  final _password = TextEditingController();
  bool _saving = false;
  bool _showPassword = false;

  @override
  void dispose() {
    _email.dispose();
    _name.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _saving) return;
    setState(() => _saving = true);
    try {
      await _service.create(
          email: _email.text, fullName: _name.text, password: _password.text);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(
                e is ApiException ? e.userMessage : 'Could not create user.')));
      }
    }
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
        title: const Text('Add user'),
        content: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              TextFormField(
                  controller: _name,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(labelText: 'Full name'),
                  validator: (v) =>
                      v == null || v.trim().isEmpty ? 'Enter a name' : null),
              TextFormField(
                  controller: _email,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(labelText: 'Email'),
                  validator: (v) => v == null || !v.contains('@')
                      ? 'Enter a valid email'
                      : null),
              TextFormField(
                  controller: _password,
                  obscureText: !_showPassword,
                  decoration: InputDecoration(
                      labelText: 'Password',
                      suffixIcon: IconButton(
                          onPressed: () =>
                              setState(() => _showPassword = !_showPassword),
                          icon: Icon(_showPassword
                              ? Icons.visibility_off
                              : Icons.visibility))),
                  validator: (v) => v == null || v.length < 8
                      ? 'Use at least 8 characters'
                      : null),
            ]),
          ),
        ),
        actions: [
          TextButton(
              onPressed: _saving ? null : () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: _saving ? null : _save,
              child: _saving
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Create')),
        ],
      );
}

class _UserDetailScreen extends StatefulWidget {
  const _UserDetailScreen({required this.user, required this.service});
  final ManagedUser user;
  final UserService service;
  @override
  State<_UserDetailScreen> createState() => _UserDetailScreenState();
}

class _UserDetailScreenState extends State<_UserDetailScreen> {
  late ManagedUser _user;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _user = widget.user;
  }

  Future<void> _edit() async {
    final name = TextEditingController(text: _user.fullName);
    final result = await showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Edit user'),
        content: TextField(
            controller: name,
            textCapitalization: TextCapitalization.words,
            decoration: const InputDecoration(labelText: 'Full name')),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(context, name.text.trim()),
              child: const Text('Save')),
        ],
      ),
    );
    name.dispose();
    if (result == null || result.isEmpty || result == _user.fullName) return;
    await _run(() async {
      _user = await widget.service.update(_user.id, fullName: result);
      if (mounted) setState(() {});
    });
  }

  Future<void> _toggleActive() async {
    await _run(() async {
      _user = await widget.service.update(_user.id, isActive: !_user.isActive);
      if (mounted) setState(() {});
    });
  }

  Future<void> _delete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Deactivate user?'),
        content: const Text(
            'The user will be deactivated. Their financial history is kept safe.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Deactivate')),
        ],
      ),
    );
    if (confirmed != true) return;
    await _run(() async {
      await widget.service.delete(_user.id);
      if (mounted) Navigator.pop(context, true);
    });
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      await action();
    } catch (e) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(e is ApiException
                ? e.userMessage
                : 'Could not complete the action.')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('User details')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
                child: ListTile(
                    leading: const Icon(Icons.person),
                    title: Text(_user.fullName),
                    subtitle: Text(_user.email))),
            Card(
                child: Column(children: [
              ListTile(
                  title: const Text('Status'),
                  trailing: Text(_user.isActive ? 'Active' : 'Inactive')),
              ListTile(
                  title: const Text('Email verification'),
                  trailing:
                      Text(_user.isEmailVerified ? 'Verified' : 'Unverified')),
              ListTile(title: const Text('Role'), trailing: Text(_user.role)),
              ListTile(
                  title: const Text('User ID'),
                  trailing: Text(_user.id.toString())),
            ])),
            const SizedBox(height: 8),
            FilledButton.icon(
                onPressed: _busy ? null : _edit,
                icon: const Icon(Icons.edit),
                label: const Text('Edit name')),
            OutlinedButton.icon(
                onPressed: _busy ? null : _toggleActive,
                icon: Icon(_user.isActive ? Icons.person_off : Icons.person),
                label: Text(_user.isActive ? 'Deactivate' : 'Reactivate')),
            const SizedBox(height: 8),
            TextButton.icon(
                onPressed: _busy ? null : _delete,
                icon: const Icon(Icons.delete_outline),
                label: const Text('Delete / deactivate')),
          ],
        ),
      );
}
