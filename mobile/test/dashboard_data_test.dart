import 'package:flutter_test/flutter_test.dart';

import 'package:money_maintainer_mobile/features/dashboard/data/dashboard_api.dart';

void main() {
  test('dashboard data holds API summary values', () {
    final data = DashboardData(
      availableMoney: 1000,
      spending: 200,
      income: 500,
      refunds: 50,
      netCashFlow: 350,
      budgetTotal: 400,
      budgetSpent: 200,
      budgetRemaining: 200,
      creditOutstanding: 100,
      moneyOwed: 300,
      moneyOwes: 50,
      officePending: 75,
      activeGoals: 2,
      goalsNearDeadline: 1,
      overdueDebts: 0,
      upcomingDebts: 1,
      unreadAlerts: 2,
      recentActivity: const [
        RecentActivity(
          type: 'EXPENSE',
          amount: 80,
          description: 'Metro',
          date: null,
        ),
      ],
      netWorth: 900,
      totalAssets: 1200,
      totalLiabilities: 300,
    );

    expect(data.availableMoney, 1000);
    expect(data.recentActivity.single.description, 'Metro');
    expect(data.unreadAlerts, 2);
  });
}
