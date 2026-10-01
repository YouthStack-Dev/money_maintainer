import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'auth_service.dart';

class ResetPasswordScreen extends StatefulWidget {
  const ResetPasswordScreen({super.key, required this.onBack});
  final VoidCallback onBack;
  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _token = TextEditingController(),
      _password = TextEditingController(),
      _confirm = TextEditingController();
  final _auth = AuthService();
  bool _loading = false, _show = false, _done = false;
  String? _error;
  @override
  void dispose() {
    _token.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final p = _password.text;
    if (_token.text.trim().isEmpty) {
      setState(() => _error = 'Reset token is required.');
      return;
    }
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
      await _auth.resetPassword(token: _token.text, password: p);
      if (mounted) setState(() => _done = true);
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
    final content = _done
        ? Column(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.lock_reset, size: 48),
            const SizedBox(height: 16),
            const Text('Password reset successfully.'),
            const SizedBox(height: 20),
            FilledButton(
                onPressed: widget.onBack, child: const Text('Back to sign in'))
          ])
        : Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
                TextField(
                    controller: _token,
                    maxLines: 3,
                    decoration:
                        const InputDecoration(labelText: 'Reset token')),
                const SizedBox(height: 16),
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
                                : Icons.visibility_outlined)))),
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
                              color: Theme.of(context).colorScheme.error))),
                const SizedBox(height: 20),
                FilledButton(
                    onPressed: _loading ? null : _submit,
                    child: _loading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2))
                        : const Text('Reset password')),
                TextButton(
                    onPressed: _loading ? null : widget.onBack,
                    child: const Text('Back to sign in'))
              ]);
    return Scaffold(
        appBar: AppBar(title: const Text('Set new password')),
        body: Center(
            child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Padding(
                    padding: const EdgeInsets.all(24), child: content))));
  }
}
