import '../../core/network/api_client.dart';

class ManagedUser {
  const ManagedUser(
      {required this.id,
      required this.email,
      required this.fullName,
      required this.role,
      required this.isActive,
      required this.isEmailVerified});
  final int id;
  final String email;
  final String fullName;
  final String role;
  final bool isActive;
  final bool isEmailVerified;
  factory ManagedUser.fromJson(Map<String, dynamic> j) => ManagedUser(
        id: (j['id'] as num).toInt(),
        email: j['email']?.toString() ?? '',
        fullName: j['full_name']?.toString() ?? '',
        role: j['role']?.toString() ?? 'USER',
        isActive: j['is_active'] != false,
        isEmailVerified: j['is_email_verified'] == true,
      );
}

class UserService {
  UserService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;

  Future<List<ManagedUser>> list() async {
    final data = await _api.get('/api/v1/users');
    return (data as List)
        .map((e) => ManagedUser.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<ManagedUser> get(int id) async {
    final data = await _api.get('/api/v1/users/$id');
    return ManagedUser.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<ManagedUser> create(
      {required String email,
      required String fullName,
      required String password}) async {
    final data = await _api.post('/api/v1/users', query: {
      'email': email.trim(),
      'full_name': fullName.trim(),
      'password': password,
    });
    return ManagedUser.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<ManagedUser> update(int id, {String? fullName, bool? isActive}) async {
    final query = <String, String>{};
    if (fullName != null) query['full_name'] = fullName.trim();
    if (isActive != null) query['is_active'] = isActive.toString();
    final data = await _api.patch('/api/v1/users/$id', query: query);
    return ManagedUser.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<void> delete(int id) async {
    await _api.delete('/api/v1/users/$id');
  }
}
