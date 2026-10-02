import 'package:flutter/material.dart';

import '../../auth/data/auth_repository.dart';
import '../../dashboard/presentation/dashboard_page.dart';
import '../../profile/presentation/profile_page.dart';
import 'shell_destination.dart';

class AppShell extends StatefulWidget {
  const AppShell({
    required this.repository,
    required this.email,
    required this.onLogout,
    super.key,
  });

  final AuthRepository repository;
  final String email;
  final Future<void> Function() onLogout;

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      DashboardPage(accessToken: widget.repository.accessToken),
      const _PlaceholderPage(
        title: 'Money',
        icon: Icons.account_balance_wallet_outlined,
      ),
      const _PlaceholderPage(
        title: 'Credit',
        icon: Icons.credit_card_outlined,
      ),
      const _PlaceholderPage(
        title: 'Lending',
        icon: Icons.handshake_outlined,
      ),
      ProfilePage(
        repository: widget.repository,
        onLogout: widget.onLogout,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Money Maintainer'),
        actions: [
          if (_selectedIndex != 4)
            IconButton(
              tooltip: 'Profile',
              onPressed: () => setState(() => _selectedIndex = 4),
              icon: const Icon(Icons.person_outline),
            ),
        ],
      ),
      body: IndexedStack(index: _selectedIndex, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() => _selectedIndex = index);
        },
        destinations: ShellDestination.values
            .map(
              (destination) => NavigationDestination(
                icon: Icon(destination.icon),
                selectedIcon: Icon(destination.selectedIcon),
                label: destination.label,
              ),
            )
            .toList(growable: false),
      ),
    );
  }
}

class _PlaceholderPage extends StatelessWidget {
  const _PlaceholderPage({required this.title, required this.icon});

  final String title;
  final IconData icon;

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 48),
              const SizedBox(height: 12),
              Text(title, style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 8),
              const Text('This section is coming next.'),
            ],
          ),
        ),
      );
}
