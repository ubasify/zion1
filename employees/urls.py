from django.urls import path
from .views import (
    HRDashboardView,
    EmployeeListView, EmployeeDetailView, EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView,
    LeaveRequestListView, LeaveRequestCreateView, LeaveRequestUpdateView,
    PayrollListView, PayrollCreateView, PayrollUpdateView,
    DocumentListView, DocumentCreateView,
)

urlpatterns = [
    # HR Dashboard
    path('', HRDashboardView.as_view(), name='hr-dashboard'),
    
    # Employee Management
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee-delete'),
    
    # Leave Management
    path('leaves/', LeaveRequestListView.as_view(), name='leave-list'),
    path('leaves/create/', LeaveRequestCreateView.as_view(), name='leave-create'),
    path('leaves/<int:pk>/edit/', LeaveRequestUpdateView.as_view(), name='leave-update'),
    
    # Payroll Management
    path('payroll/', PayrollListView.as_view(), name='payroll-list'),
    path('payroll/create/', PayrollCreateView.as_view(), name='payroll-create'),
    path('payroll/<int:pk>/edit/', PayrollUpdateView.as_view(), name='payroll-update'),
    
    # Document Management
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/upload/', DocumentCreateView.as_view(), name='document-create'),
]
