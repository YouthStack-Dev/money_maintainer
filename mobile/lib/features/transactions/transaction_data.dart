enum TransactionType { income, expense, transfer, refund }

class AccountOption {
  const AccountOption(
      {required this.id, required this.name, required this.type});
  final int id;
  final String name;
  final String type;

  factory AccountOption.fromJson(Map<String, dynamic> json) => AccountOption(
        id: (json['id'] as num).toInt(),
        name: '${json['name'] ?? ''}',
        type: '${json['account_type'] ?? ''}',
      );
}

class CategoryOption {
  const CategoryOption(
      {required this.id, required this.name, required this.type});
  final int id;
  final String name;
  final String type;

  factory CategoryOption.fromJson(Map<String, dynamic> json) => CategoryOption(
        id: (json['id'] as num).toInt(),
        name: '${json['name'] ?? ''}',
        type: '${json['category_type'] ?? ''}',
      );
}

class TransactionRecord {
  const TransactionRecord(
      {required this.id,
      required this.accountId,
      this.categoryId,
      this.transferAccountId,
      required this.type,
      required this.amount,
      this.description,
      required this.date,
      required this.active});
  final int id, accountId;
  final int? categoryId, transferAccountId;
  final TransactionType type;
  final double amount;
  final String? description;
  final DateTime date;
  final bool active;
  factory TransactionRecord.fromJson(Map<String, dynamic> j) =>
      TransactionRecord(
          id: (j['id'] as num).toInt(),
          accountId: (j['account_id'] as num).toInt(),
          categoryId: (j['category_id'] as num?)?.toInt(),
          transferAccountId: (j['transfer_account_id'] as num?)?.toInt(),
          type: TransactionType.values.firstWhere(
              (v) => v.name.toUpperCase() == '${j['transaction_type']}'),
          amount: double.tryParse('${j['amount']}') ?? 0,
          description: j['description']?.toString(),
          date: DateTime.tryParse('${j['transaction_date']}') ?? DateTime.now(),
          active: j['is_active'] == true);
}

class TransactionPayload {
  const TransactionPayload(
      {required this.accountId,
      required this.type,
      required this.amount,
      required this.date,
      this.categoryId,
      this.transferAccountId,
      this.description});

  final int accountId;
  final TransactionType type;
  final double amount;
  final DateTime date;
  final int? categoryId;
  final int? transferAccountId;
  final String? description;

  Map<String, dynamic> toJson() => {
        'account_id': accountId,
        if (categoryId != null) 'category_id': categoryId,
        if (transferAccountId != null) 'transfer_account_id': transferAccountId,
        'transaction_type': type.name.toUpperCase(),
        'amount': amount,
        if (description != null && description!.trim().isNotEmpty)
          'description': description!.trim(),
        'transaction_date': date.toUtc().toIso8601String(),
      };
}
