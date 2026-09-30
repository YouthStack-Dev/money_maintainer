import '../../core/auth/token_storage.dart';
import '../../core/network/api_client.dart';

class AuthService {
  AuthService({
    ApiClient? apiClient,
    TokenStorage? tokenStorage,
  })  : _apiClient = apiClient ?? ApiClient(tokenStorage: tokenStorage),
        _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  Future<void> register({
    required String email,
    required String fullName,
    required String password,
  }) async {
    await _apiClient.post(
      '/api/v1/auth/register',
      query: {
        'email': email.trim(),
        'full_name': fullName.trim(),
        'password': password,
      },
    );
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.post(
      '/api/v1/auth/login',
      query: {
        'email': email.trim(),
        'password': password,
      },
    );

    await _tokenStorage.save(
      accessToken: response['access_token'] as String,
      refreshToken: response['refresh_token'] as String,
    );
  }

  Future<Map<String, dynamic>> me() async {
    final response = await _apiClient.get('/api/v1/auth/me');
    return Map<String, dynamic>.from(response as Map);
  }

  Future<void> logout() async {
    final token = await _tokenStorage.refreshToken();
    if (token != null && token.isNotEmpty) {
      try {
        await _apiClient.post(
          '/api/v1/auth/logout',
          query: {'refresh_token_value': token},
        );
      } finally {
        await _tokenStorage.clear();
      }
    } else {
      await _tokenStorage.clear();
    }
  }

  Future<bool> hasSession() async {
    final token = await _tokenStorage.accessToken();
    return token != null && token.isNotEmpty;
  }
}
