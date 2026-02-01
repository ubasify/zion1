from django.urls import path
from .views import (
    AttendanceListView, AttendanceCreateView, AttendanceUpdateView, AttendanceDeleteView,
    FinancialDashboardView, IncomeListView, IncomeCreateView, ExpenseListView, ExpenseCreateView, FinancialReportView,
    LedgerView, BankAccountListView, BankAccountCreateView, BankAccountUpdateView,
    BudgetListView, BudgetCreateView, BudgetUpdateView,
    CommunityImpactListView, CommunityImpactCreateView,
    AnnouncementListView, AnnouncementCreateView
)

urlpatterns = [
    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/create/', AttendanceCreateView.as_view(), name='attendance-create'),
    path('attendance/<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('attendance/<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance-delete'),
    
    # Financial Management
    path('', FinancialDashboardView.as_view(), name='financial-dashboard'),
    path('income/', IncomeListView.as_view(), name='financial-income-list'),
    path('income/new/', IncomeCreateView.as_view(), name='financial-income-create'),
    path('expense/', ExpenseListView.as_view(), name='financial-expense-list'),
    path('expense/new/', ExpenseCreateView.as_view(), name='financial-expense-create'),
    path('reports/', FinancialReportView.as_view(), name='financial-reports'),
    path('ledger/', LedgerView.as_view(), name='financial-ledger'),
    
    # Bank Accounts
    path('accounts/', BankAccountListView.as_view(), name='bank-account-list'),
    path('accounts/new/', BankAccountCreateView.as_view(), name='bank-account-create'),
    path('accounts/<int:pk>/edit/', BankAccountUpdateView.as_view(), name='bank-account-edit'),

    # Budgets
    path('budgets/', BudgetListView.as_view(), name='budget-list'),
    path('budgets/new/', BudgetCreateView.as_view(), name='budget-create'),
    path('budgets/<int:pk>/edit/', BudgetUpdateView.as_view(), name='budget-edit'),

    # Community Impact
    path('impact/', CommunityImpactListView.as_view(), name='impact-list'),
    path('impact/new/', CommunityImpactCreateView.as_view(), name='impact-create'),

    # Announcements
    path('announcements/', AnnouncementListView.as_view(), name='announcement-list'),
    path('announcements/new/', AnnouncementCreateView.as_view(), name='announcement-create'),
]
