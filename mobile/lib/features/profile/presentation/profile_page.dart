import 'package:flutter/material.dart';

import '../../../core/errors/app_exception.dart';
import '../../auth/data/auth_api.dart';
import '../../auth/data/auth_repository.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({
    required this.repository,
    required this.initialEmail,
    required this.onLogout,
    super.key,
  });

  final AuthRepository repository;
  final String initialEmail;
  final Future<void> Function() onLogout;

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  CurrentUser? _user;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final user = await widget.repository.currentUser();
      if (!mounted) return;
      setState(() {
        _user = user;
        _error = null;
      });
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } on NetworkException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } catch (_) {
      if (mounted) setState(() => _error = 'Unable to load profile.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = _user;
    final displayEmail = user?.email.isNotEmpty == true
        ? user!.email
        : widget.initialEmail;
    return SafeArea(
      child: RefreshIndicator(
        onRefresh: _loadProfile,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
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
                      child: Text(
                        _initials(user?.fullName ?? ''),
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _loading
                                ? 'Loading profile...'
                                : user?.fullName.isNotEmpty == true
                                    ? user!.fullName
                                    : 'Money Maintainer user',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            displayEmail.isEmpty
                                ? 'Signed-in account'
                                : displayEmail,
                            overflow: TextOverflow.ellipsis,
                          ),
                          if (_error != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              _error!,
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.error,
                              ),
                            ),
                          ],
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
                  ListTile(
                    leading: const Icon(Icons.person_outline),
                    title: const Text('Email'),
                    subtitle: Text(
                      displayEmail.isEmpty ? 'Not loaded' : displayEmail,
                    ),
                  ),
                  const Divider(height: 1),
                  ListTile(
                    leading: const Icon(Icons.verified_user_outlined),
                    title: const Text('Email verification'),
                    subtitle: Text(
                      user?.isEmailVerified == true
                          ? 'Verified'
                          : 'Not verified',
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Text('Security', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Card(
              child: ListTile(
                leading: const Icon(Icons.pin_outlined),
                title: const Text('Change 4-digit PIN'),
                subtitle: const Text('Changing the PIN signs you out'),
                trailing: const Icon(Icons.chevron_right),
                onTap: _showChangePin,
              ),
            ),
            const SizedBox(height: 20),
            Text('App', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            const Card(
              child: ListTile(
                leading: Icon(Icons.info_outline),
                title: Text('About Money Maintainer'),
                subtitle: Text('Version 1.0.0'),
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
      ),
    );
  }

  Future<void> _showChangePin() async {
    final pin = TextEditingController();
    final confirm = TextEditingController();
    var obscure = true;
    var error = '';

    final value = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Change PIN'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: pin,
                keyboardType: TextInputType.number,
                obscureText: obscure,
                maxLength: 4,
                decoration: InputDecoration(
                  labelText: 'New 4-digit PIN',
                  counterText: '',
                  suffixIcon: IconButton(
                    onPressed: () => setDialogState(() => obscure = !obscure),
                    icon: Icon(
                      obscure
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: confirm,
                keyboardType: TextInputType.number,
                obscureText: obscure,
                maxLength: 4,
                decoration: const InputDecoration(
                  labelText: 'Confirm PIN',
                  counterText: '',
                ),
              ),
              if (error.isNotEmpty) ...[
                const SizedBox(height: 10),
                Text(
                  error,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () async {
                if (!RegExp(r'^\d{4}$').hasMatch(pin.text)) {
                  setDialogState(
                    () => error = 'PIN must be exactly 4 digits.',
                  );
                  return;
                }
                if (pin.text != confirm.text) {
                  setDialogState(() => error = 'PINs do not match.');
                  return;
                }
                try {
                  await widget.repository.changePin(pin.text);
                  if (dialogContext.mounted) {
                    Navigator.pop(dialogContext, true);
                  }
                } on ApiException catch (e) {
                  setDialogState(() => error = e.message);
                } on NetworkException catch (e) {
                  setDialogState(() => error = e.message);
                } catch (_) {
                  setDialogState(() => error = 'Unable to change PIN.');
                }
              },
              child: const Text('Change PIN'),
            ),
          ],
        ),
      ),
    );
    pin.dispose();
    confirm.dispose();

    if (value == true && mounted) await widget.onLogout();
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
    if (confirmed == true) await widget.onLogout();
  }

  String _initials(String name) {
    final parts =
        name.trim().split(RegExp(r'\s+')).where((p) => p.isNotEmpty);
    final list = parts.toList(growable: false);
    if (list.isEmpty) return 'MM';
    if (list.length == 1) return list.first.substring(0, 1).toUpperCase();
    return (list.first[0] + list.last[0]).toUpperCase();
  }
}
