class QuickEntryCandidate {
  const QuickEntryCandidate({required this.text, this.transactionType, this.amount, this.description, this.categoryName, this.accountName, this.transactionDate, required this.confidence, required this.missing, this.reason});
  final String text;
  final String? transactionType, description, categoryName, accountName, transactionDate, reason;
  final double? amount;
  final QuickEntryConfidence confidence;
  final List<String> missing;

  factory QuickEntryCandidate.fromJson(Map<String, dynamic> data) => QuickEntryCandidate(
    text: '${data['text'] ?? ''}',
    transactionType: data['transaction_type']?.toString(),
    amount: double.tryParse('${data['amount'] ?? ''}'),
    description: data['description']?.toString(),
    categoryName: data['category_name']?.toString(),
    accountName: data['account_name']?.toString(),
    transactionDate: data['transaction_date']?.toString(),
    confidence: QuickEntryConfidence.values.firstWhere(
      (e) => e.name == '${data['confidence'] ?? 'LOW'}',
      orElse: () => QuickEntryConfidence.LOW,
    ),
    missing: (data['missing'] as List? ?? []).map((e) => '$e').toList(),
    reason: data['reason']?.toString(),
  );
}

enum QuickEntryConfidence { HIGH, MEDIUM, LOW }

class QuickEntryResult {
  const QuickEntryResult({required this.status, required this.candidates, required this.transactionIds});
  final String status;
  final List<QuickEntryCandidate> candidates;
  final List<int> transactionIds;

  factory QuickEntryResult.fromJson(Map<String, dynamic> data) => QuickEntryResult(
    status: '${data['status'] ?? 'NEEDS_CONFIRMATION'}',
    candidates: (data['candidates'] as List? ?? []).map((e) => QuickEntryCandidate.fromJson(Map<String, dynamic>.from(e as Map))).toList(),
    transactionIds: (data['transaction_ids'] as List? ?? []).map((e) => (e as num).toInt()).toList(),
  );
}
