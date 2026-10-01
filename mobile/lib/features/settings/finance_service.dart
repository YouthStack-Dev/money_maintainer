import '../../core/network/api_client.dart';

class FinanceAccount {
  const FinanceAccount(
      {required this.id,
      required this.name,
      required this.type,
      required this.balance,
      this.institution});
  final int id;
  final String name;
  final String type;
  final double balance;
  final String? institution;
  factory FinanceAccount.fromJson(Map<String, dynamic> j) => FinanceAccount(
        id: (j['id'] as num).toInt(),
        name: '${j['name'] ?? ''}',
        type: '${j['account_type'] ?? ''}',
        balance: double.tryParse('${j['opening_balance'] ?? 0}') ?? 0,
        institution: j['institution_name'] as String?,
      );
}

class FinanceCategory {
  const FinanceCategory(
      {required this.id,
      required this.name,
      required this.type,
      this.parentId,
      this.isActive = true});
  final bool isActive;
  final int id;
  final String name;
  final String type;
  final int? parentId;
  factory FinanceCategory.fromJson(Map<String, dynamic> j) => FinanceCategory(
        id: (j['id'] as num).toInt(),
        name: '${j['name'] ?? ''}',
        type: '${j['category_type'] ?? ''}',
        parentId: (j['parent_id'] as num?)?.toInt(),
        isActive: j['is_active'] != false,
      );
}

class FinanceService {
  FinanceService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;
  Future<List<FinanceAccount>> accounts() async {
    final data = await _api.get('/api/v1/accounts');
    return (data as List)
        .map(
            (e) => FinanceAccount.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<List<FinanceCategory>> categories() async {
    final data = await _api.get('/api/v1/categories');
    return (data as List)
        .map((e) =>
            FinanceCategory.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<FinanceAccount> getAccount(int id) async {
    final data = await _api.get('/api/v1/accounts/$id');
    return FinanceAccount.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<FinanceAccount> updateAccount(int id,
      {String? name,
      String? institution,
      double? openingBalance,
      bool? isActive,
      String? currency}) async {
    final body = <String, dynamic>{};
    if (name != null) body['name'] = name.trim();
    if (institution != null)
      body['institution_name'] =
          institution.trim().isEmpty ? null : institution.trim();
    if (openingBalance != null) body['opening_balance'] = openingBalance;
    if (isActive != null) body['is_active'] = isActive;
    if (currency != null) body['currency'] = currency;
    final data = await _api.patch('/api/v1/accounts/$id', body: body);
    return FinanceAccount.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<void> deleteAccount(int id) async {
    await _api.delete('/api/v1/accounts/$id');
  }

  Future<void> createAccount(
      {required String name,
      required String type,
      required double openingBalance,
      String? institution}) async {
    await _api.post('/api/v1/accounts', body: {
      'name': name.trim(),
      'account_type': type,
      'opening_balance': openingBalance,
      if (institution?.trim().isNotEmpty == true)
        'institution_name': institution!.trim(),
      'currency': 'INR'
    });
  }

  Future<FinanceCategory> getCategory(int id) async {
    final data = await _api.get('/api/v1/categories/$id');
    return FinanceCategory.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<FinanceCategory> updateCategory(int id,
      {String? name,
      String? type,
      int? parentId,
      bool? isActive,
      bool setParent = false}) async {
    final body = <String, dynamic>{};
    if (name != null) body['name'] = name.trim();
    if (type != null) body['category_type'] = type;
    if (setParent) body['parent_id'] = parentId;
    if (isActive != null) body['is_active'] = isActive;
    final data = await _api.patch('/api/v1/categories/$id', body: body);
    return FinanceCategory.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<void> deleteCategory(int id) async {
    await _api.delete('/api/v1/categories/$id');
  }

  Future<void> createCategory(
      {required String name, required String type, int? parentId}) async {
    await _api.post('/api/v1/categories', body: {
      'name': name.trim(),
      'category_type': type,
      if (parentId != null) 'parent_id': parentId
    });
  }
}
