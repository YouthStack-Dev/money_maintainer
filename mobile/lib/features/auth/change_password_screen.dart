import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'auth_service.dart';

class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({super.key, required this.onChanged});
  final VoidCallback onChanged;
  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _password = TextEditingController(), _confirm = TextEditingController();
  final _auth = AuthService();
  bool _loading = false, _show = false;
  String? _error;
  @override
  void dispose() {
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final p = _password.text;
    if (p.length < 12 || p.length > 128) {
      setState(() => _error = 'Password must be 12-128 characters.');
      return;
    }
    if (p != _confirm.text) {
      setState(() => _error = 'Passwords do not match.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await _auth.changePassword(p);
      if (mounted) {
        await showDialog<void>(
            context: context,
            builder: (_) => const AlertDialog(
                title: Text('Password changed'),
                content: Text(
                    'For your security, you have been signed out. Please sign in with your new password.')));
        widget.onChanged();
      }
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.userMessage);
    } on ApiNetworkException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Change password')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('Choose a new password for your account.'),
                const SizedBox(height: 20),
                TextField(
                  controller: _password,
                  obscureText: !_show,
                  decoration: InputDecoration(
                    labelText: 'New password',
                    helperText: 'Use 12-128 characters.',
                    suffixIcon: IconButton(
                      onPressed: () => setState(() => _show = !_show),
                      icon: Icon(_show
                          ? Icons.visibility_off_outlined
                          : Icons.visibility_outlined),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                    controller: _confirm,
                    obscureText: !_show,
                    decoration:
                        const InputDecoration(labelText: 'Confirm password')),
                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Text(_error!,
                        style: TextStyle(
                            color: Theme.of(context).colorScheme.error)),
                  ),
                const SizedBox(height: 20),
                FilledButton(
                  onPressed: _loading ? null : _submit,
                  child: _loading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Change password'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
