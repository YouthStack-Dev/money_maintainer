import '../../core/network/api_client.dart';
import 'home_data.dart';

class HomeService {
  HomeService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();
  final ApiClient _apiClient;

  Future<HomeData> load() async {
    final response = await _apiClient.get('/api/v1/personal-finance-home');
    return HomeData.fromJson(Map<String, dynamic>.from(response as Map));
  }
}
