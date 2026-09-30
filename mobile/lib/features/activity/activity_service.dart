import '../../core/network/api_client.dart';
import 'activity_data.dart';

class ActivityService {
  ActivityService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();
  final ApiClient _apiClient;

  Future<List<ActivityTransaction>> load({String? type}) async {
    final response = await _apiClient.get('/api/v1/transactions');
    final rows = (response as List).map((e) => ActivityTransaction.fromJson(Map<String, dynamic>.from(e as Map)));
    final active = rows.where((e) => e.active).toList();
    if (type == null) return active;
    return active.where((e) => e.type == type).toList();
  }
}
