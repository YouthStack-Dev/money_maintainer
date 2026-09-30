import '../../core/network/api_client.dart';
import 'quick_entry_data.dart';

class QuickEntryService {
  QuickEntryService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();
  final ApiClient _apiClient;

  Future<QuickEntryResult> submit(String text) async {
    final response = await _apiClient.post('/api/v1/quick-entry', body: {'text': text});
    return QuickEntryResult.fromJson(Map<String, dynamic>.from(response as Map));
  }
}
