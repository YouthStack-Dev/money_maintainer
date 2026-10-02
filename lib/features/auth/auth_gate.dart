import 'package:flutter/material.dart';

import '../home/home_screen.dart';
import '../../core/network/api_client.dart';
import 'auth_service.dart';
import 'login_screen.dart';
import 'register_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final _auth = AuthService();
  late Future<bool> _session;
  bool _showRegister = false;

  @override
  void initState() {
    super.initState();
    _session = _restoreSession();
  }

  Future<bool> _restoreSession() async {
    if (!await _auth.hasSession()) return false;
    try {
      await _auth.me();
      return true;
    } on ApiException catch (error) {
      if (error.statusCode != 401) return true;
      try {
        await _auth.refresh();
        await _auth.me();
        return true;
      } catch (_) {
        await _auth.logout();
        return false;
      }
    } catch (_) {
      return true;
    }
  }

  void _loggedIn() {
    if (!mounted) return;
    setState(() => _session = Future.value(true));
  }

  void _showRegistration() {
    if (!mounted) return;
    setState(() => _showRegister = true);
  }

  void _showLogin() {
    if (!mounted) return;
    setState(() => _showRegister = false);
  }

  void _registered() {
    if (!mounted) return;
    setState(() => _showRegister = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Account created. You can now sign in.'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: _session,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.data == true) {
          return HomeScreen(onLoggedOut: () {
            if (!mounted) return;
            setState(() => _session = Future.value(false));
          });
        }
        if (_showRegister) {
          return RegisterScreen(
            onRegistered: _registered,
            onBackToLogin: _showLogin,
          );
        }
        return LoginScreen(
          onLoggedIn: _loggedIn,
          onRegister: _showRegistration,
        );
      },
    );
  }
}
