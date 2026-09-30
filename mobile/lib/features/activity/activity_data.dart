class ActivityTransaction {
  const ActivityTransaction({required this.id, required this.type, required this.amount, this.description, required this.date, required this.active});
  final int id;
  final String type;
  final double amount;
  final String? description;
  final DateTime date;
  final bool active;

  factory ActivityTransaction.fromJson(Map<String, dynamic> data) => ActivityTransaction(
    id: (data['id'] as num).toInt(),
    type: '${data['transaction_type'] ?? ''}',
    amount: double.tryParse('${data['amount'] ?? 0}') ?? 0,
    description: data['description']?.toString(),
    date: DateTime.tryParse('${data['transaction_date']}') ?? DateTime.fromMillisecondsSinceEpoch(0),
    active: data['is_active'] == true,
  );
}

class ActivityFilter {
  const ActivityFilter(this.label, this.value);
  final String label;
  final String? value;
}
