from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.db.models import Avg, Sum, Count, Q, Value, CharField
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import TruncMonth
from .models import Attendance, Finance, Expense, BankAccount, Budget
from ministry.models import Service, Event
from people.models import Member
from .forms import AttendanceForm, IncomeForm, ExpenseForm
from datetime import timedelta
import json
from django.shortcuts import render, get_object_or_404, redirect

class AttendanceListView(ListView):
    model = Attendance
    template_name = "operations/attendance_list_refactored.html"
    context_object_name = "records"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Date Range Filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        # 2. Service Type Filter / Tab Logic
        # Priority: 'type' param (Tabs) -> 'service_type' param (Legacy/Direct)
        tab_type = self.request.GET.get('type')
        service_type = self.request.GET.get('service_type')

        if tab_type:
            if tab_type == 'sunday':
                queryset = queryset.filter(service_type__icontains='Sunday')
            elif tab_type == 'midweek':
                queryset = queryset.filter(service_type__icontains='Midweek')
            elif tab_type == 'special':
                queryset = queryset.filter(service_type__icontains='Special')
            # 'all' does nothing, shows full list
        elif service_type:
            # Fallback for old links or specific searches
            queryset = queryset.filter(service_type__icontains=service_type)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stats Calculation
        now = timezone.now().date()
        month_start = now.replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        
        # Avg Sunday Attendance (Last 12 Sundays)
        recent_sundays = Attendance.objects.filter(service_type__icontains='Sunday').order_by('-date')[:12]
        avg_sunday = recent_sundays.aggregate(avg=Avg('total_count'))['avg'] or 0
        
        # First Timers (This Month)
        ft_this_month = Attendance.objects.filter(date__gte=month_start).aggregate(sum=Sum('first_timers_count'))['sum'] or 0
        
        # Growth Rate (This Month vs Last Month Total Attendance)
        att_this_month = Attendance.objects.filter(date__gte=month_start).aggregate(sum=Sum('total_count'))['sum'] or 0
        att_last_month = Attendance.objects.filter(date__gte=last_month_start, date__lt=month_start).aggregate(sum=Sum('total_count'))['sum'] or 0
        
        growth_rate = 0
        if att_last_month > 0:
            growth_rate = ((att_this_month - att_last_month) / att_last_month) * 100
            
        # Services Recorded (Total count)
        services_count = Attendance.objects.count()

        context['stats'] = {
            'avg_sunday': int(avg_sunday),
            'first_timers_month': int(ft_this_month),
            'growth_rate': round(growth_rate, 1),
            'services_recorded': services_count
        }
        
        # Pass filters back to context
        context['current_tab'] = self.request.GET.get('type', 'all')
        context['filters'] = {
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        
        return context


class AttendanceCreateView(CreateView):
    model = Attendance
    fields = ['date', 'service_type', 'adult_count', 'children_count', 'first_timers_count', 'parish', 'ministry', 'event']
    success_url = reverse_lazy('attendance-list')

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Attendance record created successfully',
                'record': {
                    'id': self.object.id,
                    'date': self.object.date.strftime('%Y-%m-%d'),
                    'service_type': self.object.service_type,
                    'adult_count': self.object.adult_count,
                    'children_count': self.object.children_count,
                    'first_timers_count': self.object.first_timers_count,
                    'total_count': self.object.total_count,
                }
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)


class AttendanceUpdateView(UpdateView):
    model = Attendance
    fields = ['date', 'service_type', 'adult_count', 'children_count', 'first_timers_count', 'parish', 'ministry', 'event']
    success_url = reverse_lazy('attendance-list')

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Attendance record updated successfully',
                'record': {
                    'id': self.object.id,
                    'date': self.object.date.strftime('%Y-%m-%d'),
                    'service_type': self.object.service_type,
                    'adult_count': self.object.adult_count,
                    'children_count': self.object.children_count,
                    'first_timers_count': self.object.first_timers_count,
                    'total_count': self.object.total_count,
                }
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)


class AttendanceDeleteView(DeleteView):
    model = Attendance
    success_url = reverse_lazy('attendance-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Attendance record deleted successfully'
            })
        return super().delete(request, *args, **kwargs)

# --- FINANCIAL MANAGEMENT ---

class FinancialDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "operations/financial_dashboard_v9.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Calculate Aggregates
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        context['current_month_name'] = now.strftime('%B')
        
        income_ytd = Finance.objects.filter(date__year=current_year).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_ytd = Expense.objects.filter(date__year=current_year).aggregate(Sum('amount'))['amount__sum'] or 0
        
        income_month = Finance.objects.filter(date__year=current_year, date__month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_month = Expense.objects.filter(date__year=current_year, date__month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
        
        net_income = income_ytd - expense_ytd
        
        # 2. Format Strings (Logic moved to backend)
        def fmt(val):
            try:
                v = float(val)
                # Handle negative values for formatting if needed, but here we format magnitude
                # Context handles the sign for net income coloring.
                prefix = ""
                if v < 0:
                    v = abs(v)
                    prefix = "-"
                
                s = ""
                if v >= 1_000_000_000: s = f"{v/1_000_000_000:.1f}B"
                elif v >= 1_000_000: s = f"{v/1_000_000:.1f}M"
                elif v >= 1_000: s = f"{v/1_000:.1f}k"
                else: s = f"{v:,.0f}"
                
                return f"{prefix}£{s}"
            except:
                return "0"

        context['fmt_income_ytd'] = fmt(income_ytd)
        context['fmt_expense_ytd'] = fmt(expense_ytd)
        context['fmt_net_income'] = fmt(net_income)
        context['fmt_income_month'] = fmt(income_month)
        context['fmt_expense_month'] = fmt(expense_month)
        
        eff = 0
        if income_ytd > 0:
            eff = (expense_ytd / income_ytd) * 100
        context['fmt_efficiency'] = f"{eff:.1f}"
        
        context['is_net_positive'] = (net_income >= 0)
        
        # 3. Recent Transactions (Combined)
        inflows = Finance.objects.all().annotate(
            type=Value('Income', output_field=CharField())
        ).order_by('-date')[:10]
        
        outflows = Expense.objects.all().annotate(
            type=Value('Expense', output_field=CharField())
        ).order_by('-date')[:10]
        
        from itertools import chain
        from operator import attrgetter
        
        # Combine and Sort (Top 10 most recent)
        recent_transactions = sorted(
            chain(inflows, outflows),
            key=attrgetter('date'),
            reverse=True
        )[:10]

        context['recent_transactions'] = recent_transactions
        return context

# --- LEDGER & RELATED TABLES ---

class LedgerView(LoginRequiredMixin, TemplateView):
    template_name = "operations/ledger.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q', '')
        
        # Fetch all records
        inflows = Finance.objects.all()
        outflows = Expense.objects.all()

        if q:
            inflows = inflows.filter(
                Q(category__icontains=q) | 
                Q(description__icontains=q) |
                Q(member__first_name__icontains=q) |
                Q(member__last_name__icontains=q)
            )
            outflows = outflows.filter(
                Q(category__icontains=q) | 
                Q(description__icontains=q)
            )

        inflows = inflows.annotate(type=Value('Income', output_field=CharField()))
        outflows = outflows.annotate(type=Value('Expense', output_field=CharField()))
        
        # Combine and Sort
        from itertools import chain
        from operator import attrgetter
        
        transactions = sorted(
            chain(inflows, outflows),
            key=attrgetter('date'),
            reverse=True
        )
        
        context['transactions'] = transactions
        return context

class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = "operations/bank_account_list.html"
    context_object_name = "bank_accounts"

    def get_queryset(self):
        return BankAccount.objects.all().order_by('name')

class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    template_name = "operations/bank_account_form.html"
    fields = ['name', 'account_number', 'bank_name', 'currency', 'current_balance']
    success_url = reverse_lazy('bank-account-list')

class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccount
    template_name = "operations/bank_account_form.html"
    fields = ['name', 'account_number', 'bank_name', 'currency', 'current_balance']
    success_url = reverse_lazy('bank-account-list')

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = "operations/budget_list.html"
    context_object_name = "budgets"

    def get_queryset(self):
        return Budget.objects.all().order_by('year', 'category')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate utilization for each budget
        # This is a bit complex without aggregation, ensuring we match category and year
        # For MVP, we pass simple objects. Advanced: annotate actual spent
        return context

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    template_name = "operations/budget_form.html"
    fields = ['category', 'year', 'amount', 'start_date', 'end_date', 'description']
    success_url = reverse_lazy('budget-list')

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    template_name = "operations/budget_form.html"
    fields = ['category', 'year', 'amount', 'start_date', 'end_date', 'description']
    success_url = reverse_lazy('budget-list')



class IncomeListView(LoginRequiredMixin, ListView):
    model = Finance
    template_name = "operations/income_list.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        category = self.request.GET.get('category')
        
        if date_from: qs = qs.filter(date__gte=date_from)
        if date_to: qs = qs.filter(date__lte=date_to)
        if category: qs = qs.filter(category__icontains=category)
        
        return qs.order_by('-date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Unique categories for filter dropdown
        ctx['categories'] = Finance.objects.values_list('category', flat=True).distinct()
        return ctx

class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Finance
    form_class = IncomeForm
    template_name = "operations/form_modal.html" # Reusing a generic modal form or creating specific
    success_url = reverse_lazy('financial-income-list')
    
    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = "operations/expense_list.html"
    context_object_name = "expenses"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        category = self.request.GET.get('category')
        
        if date_from: qs = qs.filter(date__gte=date_from)
        if date_to: qs = qs.filter(date__lte=date_to)
        if category: qs = qs.filter(category__icontains=category)
        
        return qs.order_by('-date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Expense.objects.values_list('category', flat=True).distinct()
        return ctx

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "operations/form_modal.html"
    success_url = reverse_lazy('financial-expense-list')

class FinancialReportView(LoginRequiredMixin, TemplateView):
    template_name = "operations/financial_reports_v6.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        report_type = self.request.GET.get('type', 'pnl') # pnl, monthly, category
        year = int(self.request.GET.get('year', timezone.now().year))
        
        ctx['year'] = year
        ctx['report_type'] = report_type
        
        # Boolean flags for logic-less template
        ctx['is_pnl'] = (report_type == 'pnl')
        ctx['is_monthly'] = (report_type == 'monthly')
        
        # Boolean flags for years (simple approach for now)
        ctx['is_2024'] = (year == 2024)
        ctx['is_2025'] = (year == 2025)
        ctx['is_2026'] = (year == 2026)
        
        start_date = timezone.datetime(year, 1, 1)
        end_date = timezone.datetime(year, 12, 31)
        
        # Format Helper
        def fmt_curr(val):
            try:
                v = float(val)
                is_neg = v < 0
                v = abs(v)
                s = f"{v:,.2f}"
                return f"-£{s}" if is_neg else f"£{s}"
            except:
                return "£0.00"

        if report_type == 'pnl':
            # Simple P&L Aggregate
            income = Finance.objects.filter(date__year=year).aggregate(total=Sum('amount'))['total'] or 0
            expense = Expense.objects.filter(date__year=year).aggregate(total=Sum('amount'))['total'] or 0
            net = income - expense
            ctx['pnl'] = {
                'income': fmt_curr(income),
                'expense': fmt_curr(expense),
                'net': fmt_curr(net),
                'is_net_positive': net >= 0
            }
            
        elif report_type == 'monthly':
            # Monthly Breakdown
            income_qs = Finance.objects.filter(date__year=year).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
            expense_qs = Expense.objects.filter(date__year=year).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
            
            # Merge into a list of 12 months
            data = []
            for i in range(1, 13):
                m_date = timezone.datetime(year, i, 1).date()
                inc = next((item['total'] for item in income_qs if item['month'].month == i), 0)
                exp = next((item['total'] for item in expense_qs if item['month'].month == i), 0)
                net = inc - exp
                data.append({
                    'month_name': m_date.strftime('%B'),
                    'income': fmt_curr(inc),
                    'expense': fmt_curr(exp),
                    'net': fmt_curr(net),
                    'is_net_positive': net >= 0
                })
            ctx['monthly_data'] = data
            
        return ctx
