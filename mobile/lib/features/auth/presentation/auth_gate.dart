import 'package:flutter/material.dart';

import '../../../core/config/app_environment.dart';
import '../../../core/errors/app_exception.dart';
import '../../shell/presentation/app_shell.dart';
import '../data/auth_repository.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  late final AuthRepository _repository;
  bool _loading = true;
  bool _authenticated = false;
  String _email = '';

  @override
  void initState() {
    super.initState();
    _repository = AuthRepository(config: AppEnvironmentConfig.development);
    _restore();
  }

  Future<void> _restore() async {
    final session = await _repository.restoreSession();
    if (!mounted) return;
    if (session != null) _email = await _repository.savedEmail;
    setState(() {
      _authenticated = session != null;
      _loading = false;
    });
  }

  Future<void> _authenticatedNow() async {
    _email = await _repository.savedEmail;
    if (mounted) setState(() => _authenticated = true);
  }

  Future<void> _logout() async {
    await _repository.logout();
    if (mounted) {
      setState(() {
        _authenticated = false;
        _email = '';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    if (_authenticated) {
      return AppShell(email: _email, onLogout: _logout);
    }
    return AuthScreen(
      repository: _repository,
      onAuthenticated: _authenticatedNow,
    );
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({
    required this.repository,
    required this.onAuthenticated,
    super.key,
  });

  final AuthRepository repository;
  final Future<void> Function() onAuthenticated;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _name = TextEditingController();
  final _pin = TextEditingController();
  bool _registering = false;
  bool _loading = false;
  bool _obscurePin = true;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _name.dispose();
    _pin.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      if (_registering) {
        await widget.repository.register(
          email: _email.text,
          fullName: _name.text,
          pin: _pin.text,
        );
      } else {
        await widget.repository.login(email: _email.text, pin: _pin.text);
      }
      if (mounted) await widget.onAuthenticated();
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = _friendlyError(e));
    } on NetworkException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } catch (_) {
      if (mounted) {
        setState(() => _error = 'Something went wrong. Please try again.');
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _friendlyError(ApiException e) {
    switch (e.statusCode) {
      case 401: return 'Invalid email or PIN.';
      case 403: return 'Email verification is required.';
      case 409: return 'An account with this email already exists.';
      case 422: return e.message;
      case 429: return 'Too many failed attempts. Please try again later.';
      case 503: return 'The service is temporarily unavailable.';
      default: return e.message;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('Money Maintainer',
                        style: Theme.of(context).textTheme.headlineMedium),
                    const SizedBox(height: 8),
                    Text(_registering ? 'Create account' : 'Welcome back'),
                    const SizedBox(height: 32),
                    if (_error != null) ...[
                      Text(_error!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          )),
                      const SizedBox(height: 16),
                    ],
                    if (_registering) ...[
                      TextFormField(
                        controller: _name,
                        textInputAction: TextInputAction.next,
                        decoration:
                            const InputDecoration(labelText: 'Full name'),
                        validator: (v) => v == null || v.trim().isEmpty
                            ? 'Enter your name'
                            : null,
                      ),
                      const SizedBox(height: 16),
                    ],
                    TextFormField(
                      controller: _email,
                      keyboardType: TextInputType.emailAddress,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(labelText: 'Email'),
                      validator: (v) =>
                          (v?.trim().contains('@') ?? false)
                              ? null
                              : 'Enter a valid email',
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _pin,
                      keyboardType: TextInputType.number,
                      obscureText: _obscurePin,
                      maxLength: 4,
                      textInputAction: TextInputAction.done,
                      decoration: InputDecoration(
                        labelText: '4-digit PIN',
                        counterText: '',
                        suffixIcon: IconButton(
                          onPressed: () =>
                              setState(() => _obscurePin = !_obscurePin),
                          icon: Icon(_obscurePin
                              ? Icons.visibility_outlined
                              : Icons.visibility_off_outlined),
                        ),
                      ),
                      validator: (v) =>
                          v != null &&
                                  v.length == 4 &&
                                  int.tryParse(v) != null
                              ? null
                              : 'PIN must be exactly 4 digits',
                      onFieldSubmitted: (_) => _submit(),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: _loading ? null : _submit,
                      child: _loading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Text(_registering ? 'Create account' : 'Login'),
                    ),
                    const SizedBox(height: 12),
                    TextButton(
                      onPressed: _loading
                          ? null
                          : () => setState(() {
                                _registering = !_registering;
                                _error = null;
                              }),
                      child: Text(_registering
                          ? 'Already have an account? Login'
                          : 'New here? Create account'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
