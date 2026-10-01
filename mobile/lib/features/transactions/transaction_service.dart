import '../../core/network/api_client.dart';
import 'transaction_data.dart';

class TransactionService {
  TransactionService({ApiClient? apiClient}) : _api = apiClient ?? ApiClient();
  final ApiClient _api;

  Future<List<AccountOption>> accounts() async {
    final data = await _api.get('/api/v1/accounts');
    return (data as List)
        .map((e) => AccountOption.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<List<CategoryOption>> categories() async {
    final data = await _api.get('/api/v1/categories');
    return (data as List)
        .map(
            (e) => CategoryOption.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<void> create(TransactionPayload payload) async {
    await _api.post('/api/v1/transactions', body: payload.toJson());
  }

  Future<TransactionRecord> get(int id) async {
    final data = await _api.get('/api/v1/transactions/$id');
    return TransactionRecord.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<TransactionRecord> update(int id, TransactionPayload payload) async {
    final data =
        await _api.patch('/api/v1/transactions/$id', body: payload.toJson());
    return TransactionRecord.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<void> delete(int id) async {
    await _api.delete('/api/v1/transactions/$id');
  }
}
