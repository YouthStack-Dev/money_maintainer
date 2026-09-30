class HomeData {
  const HomeData({
    required this.availableMoney, required this.spending, required this.income,
    required this.netCashFlow, required this.budgetRemaining,
    required this.creditCardOutstanding, required this.moneyOwedToUser,
    required this.moneyUserOwes, required this.officePending,
    required this.activeGoalCount, required this.goalsNearDeadline,
    required this.overdueDebtCount, required this.upcomingDebtCount,
    required this.unreadAlertCount, required this.topSpendingCategories,
    required this.upcomingObligations, required this.recentActivity,
  });

  final double availableMoney, spending, income, netCashFlow, budgetRemaining;
  final double creditCardOutstanding, moneyOwedToUser, moneyUserOwes, officePending;
  final int activeGoalCount, goalsNearDeadline, overdueDebtCount, upcomingDebtCount, unreadAlertCount;
  final List<Map<String, dynamic>> topSpendingCategories, upcomingObligations, recentActivity;

  factory HomeData.fromJson(Map<String, dynamic> json) {
    double money(String key) => double.tryParse('${json[key] ?? 0}') ?? 0;
    List<Map<String, dynamic>> list(String key) =>
        (json[key] as List? ?? []).map((e) => Map<String, dynamic>.from(e as Map)).toList();

    return HomeData(
      availableMoney: money('available_money'),
      spending: money('current_month_spending'),
      income: money('current_month_income'),
      netCashFlow: money('current_month_net_cash_flow'),
      budgetRemaining: money('budget_remaining'),
      creditCardOutstanding: money('credit_card_outstanding'),
      moneyOwedToUser: money('money_owed_to_user'),
      moneyUserOwes: money('money_user_owes'),
      officePending: money('office_reimbursement_pending'),
      activeGoalCount: (json['active_goal_count'] as num?)?.toInt() ?? 0,
      goalsNearDeadline: (json['goals_near_deadline'] as num?)?.toInt() ?? 0,
      overdueDebtCount: (json['overdue_debt_count'] as num?)?.toInt() ?? 0,
      upcomingDebtCount: (json['upcoming_debt_count'] as num?)?.toInt() ?? 0,
      unreadAlertCount: (json['unread_alert_count'] as num?)?.toInt() ?? 0,
      topSpendingCategories: list('top_spending_categories'),
      upcomingObligations: list('upcoming_obligations'),
      recentActivity: list('recent_activity'),
    );
  }
}
