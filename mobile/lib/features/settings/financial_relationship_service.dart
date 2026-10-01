import '../../core/network/api_client.dart';

class RelationshipCandidate {
  const RelationshipCandidate({
    required this.text,
    this.intent,
    this.amount,
    this.personName,
    this.accountId,
    this.accountName,
    this.secondaryAccountId,
    this.secondaryAccountName,
    this.transactionDate,
    required this.confidence,
    required this.missing,
    this.reason,
  });

  final String text;
  final String? intent;
  final String? amount;
  final String? personName;
  final int? accountId;
  final String? accountName;
  final int? secondaryAccountId;
  final String? secondaryAccountName;
  final String? transactionDate;
  final String confidence;
  final List<String> missing;
  final String? reason;

  factory RelationshipCandidate.fromJson(Map<String, dynamic> json) =>
      RelationshipCandidate(
        text: json['text']?.toString() ?? '',
        intent: json['intent']?.toString(),
        amount: json['amount']?.toString(),
        personName: json['person_name']?.toString(),
        accountId: (json['account_id'] as num?)?.toInt(),
        accountName: json['account_name']?.toString(),
        secondaryAccountId: (json['secondary_account_id'] as num?)?.toInt(),
        secondaryAccountName: json['secondary_account_name']?.toString(),
        transactionDate: json['transaction_date']?.toString(),
        confidence: json['confidence']?.toString() ?? 'LOW',
        missing:
            (json['missing'] as List? ?? []).map((e) => e.toString()).toList(),
        reason: json['reason']?.toString(),
      );

  Map<String, dynamic> toJson() => {
        'text': text,
        'intent': intent,
        'amount': amount,
        'person_name': personName,
        'account_id': accountId,
        'account_name': accountName,
        'secondary_account_id': secondaryAccountId,
        'secondary_account_name': secondaryAccountName,
        'transaction_date': transactionDate,
        'confidence': confidence,
        'missing': missing,
        'reason': reason,
      };
}

class RelationshipResult {
  const RelationshipResult({
    required this.status,
    required this.candidate,
    this.transactionId,
    this.debtId,
    this.repaymentId,
  });

  final String status;
  final RelationshipCandidate candidate;
  final int? transactionId;
  final int? debtId;
  final int? repaymentId;

  factory RelationshipResult.fromJson(Map<String, dynamic> json) =>
      RelationshipResult(
        status: json['status']?.toString() ?? '',
        candidate: RelationshipCandidate.fromJson(
            Map<String, dynamic>.from(json['candidate'] as Map)),
        transactionId: (json['transaction_id'] as num?)?.toInt(),
        debtId: (json['debt_id'] as num?)?.toInt(),
        repaymentId: (json['repayment_id'] as num?)?.toInt(),
      );
}

class FinancialRelationshipService {
  FinancialRelationshipService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;

  Future<RelationshipResult> submit(
    String text, {
    bool confirm = false,
    RelationshipCandidate? candidate,
  }) async {
    final data = await _api.post(
      '/api/v1/financial-relationships',
      body: {
        'text': text.trim(),
        'confirm': confirm,
        if (candidate != null) 'candidate': candidate.toJson(),
      },
    );
    return RelationshipResult.fromJson(Map<String, dynamic>.from(data as Map));
  }
}
