import '../../../core/config/app_environment.dart';
import '../../../core/storage/secure_storage.dart';
import 'auth_api.dart';

class AuthRepository {
  AuthRepository({required AppEnvironmentConfig config, SecureStorage? storage})
      : _api = AuthApi(config: config),
        _storage = storage ?? SecureStorage();

  static const _accessTokenKey = 'auth.access_token';
  static const _refreshTokenKey = 'auth.refresh_token';
  static const _roleKey = 'auth.role';

  final AuthApi _api;
  final SecureStorage _storage;

  Future<AuthSession?> restoreSession() async {
    final token = await _storage.read(_refreshTokenKey);
    if (token == null || token.isEmpty) return null;
    try {
      final session = await _api.refresh(token);
      await _save(session);
      return session;
    } catch (_) {
      await clearSession();
      return null;
    }
  }

  Future<AuthSession> login({required String email, required String pin}) async {
    final session = await _api.login(email: email, pin: pin);
    await _save(session);
    return session;
  }

  Future<AuthSession> register({required String email, required String fullName, required String pin}) async {
    final session = await _api.register(email: email, fullName: fullName, pin: pin);
    await _save(session);
    return session;
  }

  Future<void> logout() async {
    final token = await _storage.read(_refreshTokenKey);
    if (token != null && token.isNotEmpty) {
      try { await _api.logout(token); } catch (_) {}
    }
    await clearSession();
  }

  Future<void> clearSession() async {
    await _storage.delete(_accessTokenKey);
    await _storage.delete(_refreshTokenKey);
    await _storage.delete(_roleKey);
  }

  Future<void> _save(AuthSession session) async {
    await _storage.write(_accessTokenKey, session.accessToken);
    await _storage.write(_refreshTokenKey, session.refreshToken);
    await _storage.write(_roleKey, session.role);
  }
}
