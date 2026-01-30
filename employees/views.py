from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Sum, Count, Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from core.views import SuperAdminRequiredMixin
from .models import Employee, LeaveRequest, PayrollRecord, EmployeeDocument, PerformanceReview
from ministry.models import Ministry

# ==================== HR Dashboard ====================
class HRDashboardView(SuperAdminRequiredMixin, ListView):
    """Overview dashboard for HR metrics"""
    model = Employee
    template_name = 'employees/hr_dashboard.html'
    context_object_name = 'employees'
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        """Allow user to customize page size"""
        return self.request.GET.get('per_page', 10)
    
    def get_queryset(self):
        """Filter employees based on query parameters"""
        queryset = Employee.objects.select_related('department').all()
        
        # Filter by department
        department = self.request.GET.get('department', '')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by employment type
        emp_type = self.request.GET.get('employment_type', '')
        if emp_type:
            queryset = queryset.filter(employment_type=emp_type)
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(job_title__icontains=search)
            )
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Employee metrics
        context['total_employees'] = Employee.objects.filter(status='active').count()
        context['on_leave_count'] = Employee.objects.filter(status='on_leave').count()
        context['departments'] = Ministry.objects.annotate(
            employee_count=Count('employees')
        ).order_by('-employee_count')
        
        # Leave metrics
        context['pending_leaves'] = LeaveRequest.objects.filter(status='pending').count()
        context['approved_leaves'] = LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).count()
        
        # Recent leave requests
        context['recent_leaves'] = LeaveRequest.objects.select_related('employee').order_by('-created_at')[:5]
        
        # Upcoming birthdays - Employee model doesn't have date_of_birth, use member's dob if linked
        context['upcoming_birthdays'] = Employee.objects.filter(
            member__isnull=False,
            member__dob__month=timezone.now().month
        ).select_related('member').order_by('member__dob')[:5]
        
        # Payroll summary
        current_month = timezone.now().month
        current_year = timezone.now().year
        payroll_summary = PayrollRecord.objects.filter(
            month=current_month,
            year=current_year
        ).aggregate(
            total=Sum('net_pay'),
            count=Count('id')
        )
        context['total_payroll'] = payroll_summary['total'] or 0
        context['monthly_payroll'] = payroll_summary
        
        # Filter options
        context['all_departments'] = Ministry.objects.all()
        context['selected_department'] = self.request.GET.get('department', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_employment_type'] = self.request.GET.get('employment_type', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['per_page'] = int(self.request.GET.get('per_page', 10))
        
        return context


# ==================== Employee CRUD ====================
class EmployeeListView(SuperAdminRequiredMixin, ListView):
    """List all employees with advanced filtering and sorting"""
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'user', 'member').all()
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(job_title__icontains=search)
            )
        
        # Filter by department
        department = self.request.GET.get('department', '')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by employment type
        emp_type = self.request.GET.get('employment_type', '')
        if emp_type:
            queryset = queryset.filter(employment_type=emp_type)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'last_name')
        if sort_by in ['last_name', 'hire_date', 'job_title', 'department__name']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Ministry.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['selected_department'] = self.request.GET.get('department', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_employment_type'] = self.request.GET.get('employment_type', '')
        context['sort'] = self.request.GET.get('sort', 'last_name')
        return context


class EmployeeDetailView(SuperAdminRequiredMixin, DetailView):
    """Detailed employee profile"""
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        
        # Leave history
        context['leave_requests'] = LeaveRequest.objects.filter(
            employee=employee
        ).order_by('-start_date')[:10]
        
        # Payroll history
        context['payroll_records'] = PayrollRecord.objects.filter(
            employee=employee
        ).order_by('-year', '-month')[:6]
        
        # Documents
        context['documents'] = EmployeeDocument.objects.filter(
            employee=employee
        ).order_by('-uploaded_at')
        
        # Performance reviews
        context['reviews'] = PerformanceReview.objects.filter(
            employee=employee
        ).order_by('-review_date')[:5]
        
        return context


class EmployeeCreateView(SuperAdminRequiredMixin, CreateView):
    """Create new employee"""
    model = Employee
    template_name = 'employees/employee_form.html'
    fields = [
        'employee_id', 'first_name', 'last_name', 'email', 'phone',
        'hire_date', 'department', 'job_title',
        'employment_type', 'status', 'salary_grade', 'base_salary',
        'emergency_contact_name', 'emergency_contact_phone',
        'user', 'member'
    ]
    success_url = reverse_lazy('employee-list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Employee {form.instance.first_name} {form.instance.last_name} created successfully!")
        return super().form_valid(form)


class EmployeeUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Update employee information"""
    model = Employee
    template_name = 'employees/employee_form.html'
    fields = [
        'first_name', 'last_name', 'email', 'phone',
        'hire_date', 'department', 'job_title',
        'employment_type', 'status', 'salary_grade', 'base_salary',
        'emergency_contact_name', 'emergency_contact_phone',
        'user', 'member'
    ]
    success_url = reverse_lazy('employee-list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Employee {form.instance.first_name} {form.instance.last_name} updated successfully!")
        return super().form_valid(form)


class EmployeeDeleteView(SuperAdminRequiredMixin, DeleteView):
    """Deactivate employee"""
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employee-list')
    
    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.status = 'inactive'
        employee.save()
        messages.success(request, f"Employee {employee.get_full_name} deactivated successfully!")
        return redirect(self.success_url)


# ==================== Leave Management ====================
class LeaveRequestListView(SuperAdminRequiredMixin, ListView):
    """List all leave requests"""
    model = LeaveRequest
    template_name = 'employees/leave_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = LeaveRequest.objects.select_related('employee', 'approved_by').all()
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by leave type
        leave_type = self.request.GET.get('leave_type', '')
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)
        
        # Filter by employee
        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(status='active')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_leave_type'] = self.request.GET.get('leave_type', '')
        context['selected_employee'] = self.request.GET.get('employee', '')
        return context


class LeaveRequestCreateView(SuperAdminRequiredMixin, CreateView):
    """Create new leave request"""
    model = LeaveRequest
    template_name = 'employees/leave_form.html'
    fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
    success_url = reverse_lazy('leave-list')
    
    def form_valid(self, form):
        messages.success(self.request, "Leave request created successfully!")
        return super().form_valid(form)


class LeaveRequestUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Update/Approve/Reject leave request"""
    model = LeaveRequest
    template_name = 'employees/leave_form.html'
    fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason', 'status']
    success_url = reverse_lazy('leave-list')
    
    def form_valid(self, form):
        if form.instance.status in ['approved', 'rejected']:
            form.instance.approved_by = self.request.user
        messages.success(self.request, f"Leave request {form.instance.status}!")
        return super().form_valid(form)


# ==================== Payroll Management ====================
class PayrollListView(SuperAdminRequiredMixin, ListView):
    """List all payroll records"""
    model = PayrollRecord
    template_name = 'employees/payroll_list.html'
    context_object_name = 'payroll_records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PayrollRecord.objects.select_related('employee').all()
        
        # Filter by month/year
        month = self.request.GET.get('month', '')
        year = self.request.GET.get('year', '')
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-year', '-month', 'employee__last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['selected_status'] = self.request.GET.get('status', '')
        
        # Calculate totals
        queryset = self.get_queryset()
        context['total_basic'] = queryset.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
        context['total_allowances'] = queryset.aggregate(Sum('allowances'))['allowances__sum'] or 0
        context['total_deductions'] = queryset.aggregate(Sum('deductions'))['deductions__sum'] or 0
        context['total_net'] = queryset.aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        
        return context


class PayrollCreateView(SuperAdminRequiredMixin, CreateView):
    """Generate monthly payroll"""
    model = PayrollRecord
    template_name = 'employees/payroll_form.html'
    fields = ['employee', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'net_pay', 'status']
    success_url = reverse_lazy('payroll-list')
    
    def form_valid(self, form):
        messages.success(self.request, "Payroll record created successfully!")
        return super().form_valid(form)


class PayrollUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Update payroll record"""
    model = PayrollRecord
    template_name = 'employees/payroll_form.html'
    fields = ['basic_salary', 'allowances', 'deductions', 'net_pay', 'status']
    success_url = reverse_lazy('payroll-list')
    
    def form_valid(self, form):
        messages.success(self.request, "Payroll record updated successfully!")
        return super().form_valid(form)


# ==================== Document Management ====================
class DocumentListView(SuperAdminRequiredMixin, ListView):
    """List all employee documents"""
    model = EmployeeDocument
    template_name = 'employees/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EmployeeDocument.objects.select_related('employee').all()
        
        # Filter by employee
        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by document type
        doc_type = self.request.GET.get('document_type', '')
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        return queryset.order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(status='active')
        context['selected_employee'] = self.request.GET.get('employee', '')
        context['selected_document_type'] = self.request.GET.get('document_type', '')
        return context


class DocumentCreateView(SuperAdminRequiredMixin, CreateView):
    """Upload employee document"""
    model = EmployeeDocument
    template_name = 'employees/document_form.html'
    fields = ['employee', 'document_type', 'file', 'description']
    success_url = reverse_lazy('document-list')
    
    def form_valid(self, form):
        messages.success(self.request, "Document uploaded successfully!")
        return super().form_valid(form)
