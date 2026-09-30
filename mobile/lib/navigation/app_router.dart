import 'package:flutter/material.dart';
import '../features/auth/login_screen.dart';
import '../features/home/home_screen.dart';

class AppRouter {
  const AppRouter._();
  static const login = '/login';
  static const home = '/';

  static final routes = <String, WidgetBuilder>{
    login: (_) => LoginScreen(onLoggedIn: () {}),
    home: (_) => const HomeScreen(),
  };
}
