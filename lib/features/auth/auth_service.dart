import '../../core/auth/token_storage.dart';
import '../../core/network/api_client.dart';

class AuthService {
  AuthService({ApiClient? apiClient, TokenStorage? tokenStorage})
      : _tokenStorage = tokenStorage ?? TokenStorage(),
        _apiClient = apiClient ?? ApiClient(tokenStorage: tokenStorage);

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  Future<void> register(
      {required String email,
      required String fullName,
      required String password}) async {
    final response = await _apiClient.post('/api/v1/auth/register', query: {
      'email': email.trim(),
      'full_name': fullName.trim(),
      'password': password
    });
    // Registration does not sign the user into the app; the user verifies/signs in next.
    final map = Map<String, dynamic>.from(response as Map);
    if (map['access_token'] is! String || map['refresh_token'] is! String) {
      throw const ApiException(500,
          {'detail': 'The server returned an invalid registration response.'});
    }
  }

  Future<void> login({required String email, required String password}) async {
    final response = await _apiClient.post('/api/v1/auth/login',
        query: {'email': email.trim(), 'password': password});
    await _saveTokens(response);
  }

  Future<void> refresh() async {
    final token = await _tokenStorage.refreshToken();
    if (token == null || token.isEmpty)
      throw const ApiException(401, {'detail': 'No refresh token available'});
    final response = await _apiClient
        .post('/api/v1/auth/refresh', query: {'refresh_token_value': token});
    await _saveTokens(response);
  }

  Future<void> verifyEmail(String token) async => _apiClient
      .post('/api/v1/auth/verify-email', query: {'token': token.trim()});

  Future<void> forgotPassword(String email) async => _apiClient
      .post('/api/v1/auth/forgot-password', query: {'email': email.trim()});

  Future<void> resetPassword(
          {required String token, required String password}) async =>
      _apiClient.post('/api/v1/auth/reset-password',
          query: {'token': token.trim(), 'password': password});

  Future<void> changePassword(String password) async {
    await _apiClient
        .post('/api/v1/auth/change-password', query: {'password': password});
    await _tokenStorage.clear();
  }

  Future<Map<String, dynamic>> me() async {
    final response = await _apiClient.get('/api/v1/auth/me');
    return Map<String, dynamic>.from(response as Map);
  }

  /// Clears the local session even when the remote logout request fails.
  Future<void> logout() async {
    final token = await _tokenStorage.refreshToken();
    try {
      if (token != null && token.isNotEmpty) {
        await _apiClient.post('/api/v1/auth/logout',
            query: {'refresh_token_value': token});
      }
    } catch (_) {
      // A failed remote logout must never leave the user stuck on the dashboard.
    } finally {
      await _tokenStorage.clear();
    }
  }

  Future<bool> hasSession() async =>
      (await _tokenStorage.accessToken())?.isNotEmpty == true;

  Future<void> _saveTokens(dynamic response) async {
    final map = Map<String, dynamic>.from(response as Map);
    final access = map['access_token'];
    final refresh = map['refresh_token'];
    if (access is! String ||
        access.isEmpty ||
        refresh is! String ||
        refresh.isEmpty) {
      throw const ApiException(500, {
        'detail': 'The server returned an invalid authentication response.'
      });
    }
    await _tokenStorage.save(accessToken: access, refreshToken: refresh);
  }
}
