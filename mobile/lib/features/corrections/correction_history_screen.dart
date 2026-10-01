import 'package:flutter/material.dart';
import 'correction_service.dart';

class CorrectionHistoryScreen extends StatefulWidget {
  const CorrectionHistoryScreen({super.key});
  @override
  State<CorrectionHistoryScreen> createState() =>
      _CorrectionHistoryScreenState();
}

class _CorrectionHistoryScreenState extends State<CorrectionHistoryScreen> {
  final _service = CorrectionService();
  late Future<List<CorrectionHistoryEntry>> _future;
  @override
  void initState() {
    super.initState();
    _future = _service.history();
  }

  Future<void> _refresh() async {
    setState(() => _future = _service.history());
    await _future;
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(title: const Text('Correction history')),
      body: FutureBuilder<List<CorrectionHistoryEntry>>(
        future: _future,
        builder: (c, s) {
          if (s.connectionState != ConnectionState.done)
            return const Center(child: CircularProgressIndicator());
          if (s.hasError)
            return Center(
                child: FilledButton(
                    onPressed: _refresh, child: const Text('Retry')));
          final rows = s.data!;
          if (rows.isEmpty)
            return RefreshIndicator(
                onRefresh: _refresh,
                child: ListView(children: [
                  const Padding(
                      padding: EdgeInsets.all(32),
                      child: Center(child: Text('No corrections yet.')))
                ]));
          return RefreshIndicator(
              onRefresh: _refresh,
              child: ListView.builder(
                  itemCount: rows.length,
                  itemBuilder: (_, i) {
                    final x = rows[i],
                        before = x.metadata['before'],
                        after = x.metadata['after'];
                    return Card(
                        margin: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 6),
                        child: ExpansionTile(
                            title: Text(x.action.replaceAll('_', ' ')),
                            subtitle: Text(
                                '${x.targetType ?? 'Record'} #${x.targetId ?? '-'} · ${x.createdAt.toLocal()}'),
                            children: [
                              if (before is Map)
                                ListTile(
                                    title: const Text('Before'),
                                    subtitle: Text(before.entries
                                        .map((e) => '${e.key}: ${e.value}')
                                        .join(' · '))),
                              if (after is Map)
                                ListTile(
                                    title: const Text('After'),
                                    subtitle: Text(after.entries
                                        .map((e) => '${e.key}: ${e.value}')
                                        .join(' · ')))
                            ]));
                  }));
        },
      ));
}
