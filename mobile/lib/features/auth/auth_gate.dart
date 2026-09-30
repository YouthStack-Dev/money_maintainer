import 'package:flutter/material.dart';

import 'auth_service.dart';
import 'login_screen.dart';
import '../home/home_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final _auth = AuthService();
  late Future<bool> _session;

  @override
  void initState() {
    super.initState();
    _session = _auth.hasSession();
  }

  void _loggedIn() {
    setState(() => _session = Future.value(true));
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
          return const HomeScreen();
        }
        return LoginScreen(onLoggedIn: _loggedIn);
      },
    );
  }
}
