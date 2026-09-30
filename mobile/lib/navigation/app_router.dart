import 'package:flutter/material.dart';
import '../features/home/home_screen.dart';

class AppRouter {
  const AppRouter._();

  static const home = '/';

  static final routes = <String, WidgetBuilder>{
    home: (_) => const HomeScreen(),
  };
}
