import '../../core/network/api_client.dart';

class CorrectionCandidate {
  CorrectionCandidate.fromJson(Map<String, dynamic> j)
      : text = '${j['text'] ?? ''}',
        action = j['action']?.toString(),
        transactionId = (j['transaction_id'] as num?)?.toInt(),
        duplicateTransactionId =
            (j['duplicate_transaction_id'] as num?)?.toInt(),
        reimbursementId = (j['reimbursement_id'] as num?)?.toInt(),
        amount = j['amount']?.toString(),
        transactionDate = j['transaction_date']?.toString(),
        description = j['description']?.toString(),
        accountId = (j['account_id'] as num?)?.toInt(),
        accountName = j['account_name']?.toString(),
        categoryId = (j['category_id'] as num?)?.toInt(),
        categoryName = j['category_name']?.toString(),
        confidence = j['confidence']?.toString() ?? 'LOW',
        missing = (j['missing'] as List? ?? []).map((e) => '$e').toList(),
        reason = j['reason']?.toString();
  final String text, confidence;
  final String? action,
      amount,
      transactionDate,
      description,
      accountName,
      categoryName,
      reason;
  final int? transactionId,
      duplicateTransactionId,
      reimbursementId,
      accountId,
      categoryId;
  final List<String> missing;
  Map<String, dynamic> toJson() => {
        'text': text,
        'action': action,
        'transaction_id': transactionId,
        'duplicate_transaction_id': duplicateTransactionId,
        'reimbursement_id': reimbursementId,
        'amount': amount,
        'transaction_date': transactionDate,
        'description': description,
        'account_id': accountId,
        'account_name': accountName,
        'category_id': categoryId,
        'category_name': categoryName,
        'confidence': confidence,
        'missing': missing,
        'reason': reason
      };
}

class CorrectionResult {
  CorrectionResult.fromJson(Map<String, dynamic> j)
      : status = '${j['status'] ?? ''}',
        candidate = CorrectionCandidate.fromJson(
            Map<String, dynamic>.from(j['candidate'] as Map)),
        transactionId = (j['transaction_id'] as num?)?.toInt();
  final String status;
  final CorrectionCandidate candidate;
  final int? transactionId;
}

class CorrectionHistoryEntry {
  CorrectionHistoryEntry.fromJson(Map<String, dynamic> j)
      : id = (j['id'] as num).toInt(),
        action = '${j['action'] ?? ''}',
        targetType = j['target_type']?.toString(),
        targetId = j['target_id']?.toString(),
        metadata = Map<String, dynamic>.from(j['metadata'] as Map? ?? {}),
        createdAt = DateTime.parse('${j['created_at']}');
  final int id;
  final String action;
  final String? targetType, targetId;
  final Map<String, dynamic> metadata;
  final DateTime createdAt;
}

class CorrectionService {
  CorrectionService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;
  Future<CorrectionResult> submit(String text,
      {int? transactionId,
      bool confirm = false,
      CorrectionCandidate? candidate}) async {
    final d = await _api.post('/api/v1/corrections', body: {
      'text': text.trim(),
      'confirm': confirm,
      if (transactionId != null) 'transaction_id': transactionId,
      if (candidate != null) 'candidate': candidate.toJson()
    });
    return CorrectionResult.fromJson(Map<String, dynamic>.from(d as Map));
  }

  Future<List<CorrectionHistoryEntry>> history() async {
    final d = await _api.get('/api/v1/corrections/history');
    return (d as List)
        .map((e) => CorrectionHistoryEntry.fromJson(
            Map<String, dynamic>.from(e as Map)))
        .toList();
  }
}
