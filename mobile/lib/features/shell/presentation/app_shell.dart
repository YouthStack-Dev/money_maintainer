import 'package:flutter/material.dart';

import 'shell_destination.dart';

class AppShell extends StatefulWidget {
  const AppShell({this.onLogout, super.key});
  final Future<void> Function()? onLogout;
  @override State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;
  static const _pages = <Widget>[
    _PlaceholderPage(title: 'Dashboard', icon: Icons.dashboard_outlined),
    _PlaceholderPage(title: 'Money', icon: Icons.account_balance_wallet_outlined),
    _PlaceholderPage(title: 'Credit', icon: Icons.credit_card_outlined),
    _PlaceholderPage(title: 'Lending', icon: Icons.handshake_outlined),
    _PlaceholderPage(title: 'More', icon: Icons.grid_view_outlined),
  ];

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(actions: [
      if (widget.onLogout != null)
        IconButton(tooltip: 'Logout', onPressed: widget.onLogout, icon: const Icon(Icons.logout)),
    ]),
    body: IndexedStack(index: _selectedIndex, children: _pages),
    bottomNavigationBar: NavigationBar(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (index) => setState(() => _selectedIndex = index),
      destinations: ShellDestination.values.map((d) => NavigationDestination(
        icon: Icon(d.icon), selectedIcon: Icon(d.selectedIcon), label: d.label,
      )).toList(growable: false),
    ),
  );
}

class _PlaceholderPage extends StatelessWidget {
  const _PlaceholderPage({required this.title, required this.icon});
  final String title;
  final IconData icon;
  @override
  Widget build(BuildContext context) => SafeArea(
    child: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, size: 48),
      const SizedBox(height: 12),
      Text(title, style: Theme.of(context).textTheme.headlineSmall),
    ])),
  );
}
