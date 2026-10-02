import 'package:flutter/material.dart';

enum ShellDestination {
  dashboard(
    label: 'Home',
    icon: Icons.dashboard_outlined,
    selectedIcon: Icons.dashboard,
  ),
  money(
    label: 'Money',
    icon: Icons.account_balance_wallet_outlined,
    selectedIcon: Icons.account_balance_wallet,
  ),
  credit(
    label: 'Credit',
    icon: Icons.credit_card_outlined,
    selectedIcon: Icons.credit_card,
  ),
  lending(
    label: 'Lending',
    icon: Icons.handshake_outlined,
    selectedIcon: Icons.handshake,
  ),
  profile(
    label: 'Profile',
    icon: Icons.person_outline,
    selectedIcon: Icons.person,
  );

  const ShellDestination({
    required this.label,
    required this.icon,
    required this.selectedIcon,
  });

  final String label;
  final IconData icon;
  final IconData selectedIcon;
}
