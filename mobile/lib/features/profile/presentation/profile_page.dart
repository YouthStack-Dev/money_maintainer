import 'package:flutter/material.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({
    required this.email,
    required this.onLogout,
    super.key,
  });

  final String email;
  final Future<void> Function() onLogout;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
        children: [
          Text('Profile', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 32,
                    backgroundColor: scheme.primaryContainer,
                    child: Icon(Icons.person_outline,
                        size: 34, color: scheme.onPrimaryContainer),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Money Maintainer user',
                            style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 4),
                        Text(email.isEmpty ? 'Signed-in account' : email,
                            overflow: TextOverflow.ellipsis),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          Text('Account', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                const ListTile(
                  leading: Icon(Icons.person_outline),
                  title: Text('Personal details'),
                  subtitle: Text('Profile details will be connected next'),
                ),
                const Divider(height: 1),
                const ListTile(
                  leading: Icon(Icons.lock_outline),
                  title: Text('Security'),
                  subtitle: Text('PIN and session settings'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Text('App', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: const [
                ListTile(
                  leading: Icon(Icons.notifications_none),
                  title: Text('Notifications'),
                  subtitle: Text('Coming soon'),
                ),
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.info_outline),
                  title: Text('About Money Maintainer'),
                  subtitle: Text('Version 1.0.0'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: () => _confirmLogout(context),
            icon: const Icon(Icons.logout),
            label: const Text('Log out'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 15),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmLogout(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log out?'),
        content: const Text('Your local session will be cleared.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Log out'),
          ),
        ],
      ),
    );
    if (confirmed == true) await onLogout();
  }
}
