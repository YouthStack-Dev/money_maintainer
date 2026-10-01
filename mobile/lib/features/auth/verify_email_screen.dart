import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import 'auth_service.dart';

class VerifyEmailScreen extends StatefulWidget {
  const VerifyEmailScreen({super.key, required this.onBack});
  final VoidCallback onBack;
  @override
  State<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends State<VerifyEmailScreen> {
  final _token = TextEditingController();
  final _auth = AuthService();
  bool _loading = false, _done = false;
  String? _error;
  @override
  void dispose() {
    _token.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_token.text.trim().isEmpty) {
      setState(() => _error = 'Verification token is required.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await _auth.verifyEmail(_token.text);
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
            const Icon(Icons.verified_outlined, size: 48),
            const SizedBox(height: 16),
            const Text('Email verified successfully.'),
            const SizedBox(height: 20),
            FilledButton(
                onPressed: widget.onBack, child: const Text('Back to sign in'))
          ])
        : Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
                const Text('Paste the verification token from your email.'),
                const SizedBox(height: 20),
                TextField(
                    controller: _token,
                    maxLines: 3,
                    decoration:
                        const InputDecoration(labelText: 'Verification token')),
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
                        : const Text('Verify email')),
                TextButton(
                    onPressed: _loading ? null : widget.onBack,
                    child: const Text('Back to sign in'))
              ]);
    return Scaffold(
        appBar: AppBar(title: const Text('Verify email')),
        body: Center(
            child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Padding(
                    padding: const EdgeInsets.all(24), child: content))));
  }
}
