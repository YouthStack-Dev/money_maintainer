import 'package:flutter/material.dart';

import '../features/auth/login_screen.dart';
import '../features/home/home_screen.dart';
import '../features/quick_add/quick_add_screen.dart';

class AppRouter {
  static const login = '/login';
  static const home = '/home';
  static const quickAdd = '/quick-add';

  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case login:
        return MaterialPageRoute(builder: (_) => LoginScreen(onLoggedIn: () {}));
      case home:
        return MaterialPageRoute(builder: (_) => const HomeScreen());
      case quickAdd:
        return MaterialPageRoute(builder: (_) => const QuickAddScreen());
      default:
        return MaterialPageRoute(builder: (_) => const HomeScreen());
    }
  }
}
