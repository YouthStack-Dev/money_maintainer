import '../../core/network/api_client.dart';

class ConversationResult {
  ConversationResult.fromJson(Map<String, dynamic> j)
      : status = '${j['status'] ?? ''}',
        intent = '${j['intent'] ?? ''}',
        answer = '${j['answer'] ?? ''}',
        data = Map<String, dynamic>.from(j['data'] as Map? ?? {}),
        context = Map<String, dynamic>.from(j['context'] as Map? ?? {}),
        followUp = (j['follow_up'] as List? ?? []).map((e) => '$e').toList();
  final String status, intent, answer;
  final Map<String, dynamic> data, context;
  final List<String> followUp;
}

class ConversationalFinanceService {
  ConversationalFinanceService({ApiClient? api}) : _api = api ?? ApiClient();
  final ApiClient _api;
  Future<ConversationResult> ask(String text,
      {Map<String, dynamic>? context}) async {
    final d = await _api.post('/api/v1/conversational-finance',
        body: {'text': text.trim(), 'context': context ?? {}});
    return ConversationResult.fromJson(Map<String, dynamic>.from(d as Map));
  }
}
