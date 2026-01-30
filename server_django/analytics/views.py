from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from people.models import Member
from operations.models import Attendance, Finance, Expense

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # --- Filter Logic ---
        # User requested default to be 'last_year'
        period = self.request.GET.get('period', 'last_year')
        context['selected_period'] = period
        # Boolean flags to simplify template logic
        context['period_is_last_year'] = period == 'last_year'
        context['period_is_12m'] = period == '12m'
        context['period_is_ytd'] = period == 'ytd'
        context['period_is_6m'] = period == '6m'
        context['period_is_3m'] = period == '3m'
        context['period_is_1m'] = period == '1m'
        
        # Determine Date Range
        if period == '1m':
             start_date = today - timedelta(days=30)
             end_date = today
             label_text = "Last 30 Days"
        elif period == '3m':
             start_date = today - timedelta(days=90)
             end_date = today
             label_text = "Last 3 Months"
        elif period == '6m':
            start_date = today - timedelta(days=180)
            end_date = today
            label_text = "Last 6 Months"
        elif period == '12m':
            start_date = today - timedelta(days=365)
            end_date = today
            label_text = "Last 12 Months"
        elif period == 'ytd':
            start_date = today.replace(month=1, day=1)
            end_date = today
            label_text = "Year to Date"
        elif period == 'last_year':
            # Previous Calendar Year
            prev_year = today.year - 1
            start_date = today.replace(year=prev_year, month=1, day=1)
            end_date = today.replace(year=prev_year, month=12, day=31)
            label_text = f"{prev_year} (Jan - Dec)"
        else: # Fallback
            prev_year = today.year - 1
            start_date = today.replace(year=prev_year, month=1, day=1)
            end_date = today.replace(year=prev_year, month=12, day=31)
            label_text = f"{prev_year} (Jan - Dec)"
            
        context['period_label'] = label_text

        # --- KPIs (Dynamic based on Filter) ---
        context['total_members'] = Member.objects.count() # Always current
        context['total_families'] = Member.objects.filter(family__isnull=False).values('family').distinct().count()
        
        # Avg Attendance (In the selected period)
        avg_att = Attendance.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).annotate(
            real_count=Count('details')
        ).aggregate(avg=Avg('real_count'))['avg'] or 0
        context['avg_attendance'] = round(avg_att)
        
        # Income (Total in the selected period)
        total_income = Finance.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['total_income'] = total_income
        
        # Calculate growth/trend if possible? (Simulated for now or based on previous period)
        # For simple removal of hardcoding, just showing the actual data for the period is enough.

        # --- CHARTS DATA (Filtered) ---
        
        # 1. Attendance Trend
        # Filter by Range (Inclusive)
        attendance_records = Attendance.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).annotate(
            real_count=Count('details')
        ).values('date', 'real_count').order_by('date')
        
        att_labels = []
        att_data = []
        
        # Granularity Logic
        days_diff = (end_date - start_date).days
        
        if days_diff <= 90:
            # Granular: By Date
            for r in attendance_records:
                att_labels.append(r['date'].strftime('%d %b'))
                att_data.append(r['real_count'])
        else:
            # Group by Month
            att_map = {}
            for r in attendance_records:
                m_str = r['date'].strftime('%b %Y')
                att_map.setdefault(m_str, []).append(r['real_count'])
                
            curr = start_date.replace(day=1)
            # Ensure we cover the full range of months in the interval
            end_curr = end_date.replace(day=1)
            
            def add_month(d):
                if d.month == 12: return d.replace(year=d.year+1, month=1)
                return d.replace(month=d.month+1)
            
            iter_date = curr
            while iter_date <= end_curr:
                 m_label = iter_date.strftime('%b %Y')
                 att_labels.append(m_label)
                 counts = att_map.get(m_label, [])
                 avg = sum(counts) / len(counts) if counts else 0
                 att_data.append(round(avg))
                 
                 iter_date = add_month(iter_date)
            
        context['chart_attendance_labels'] = att_labels
        context['chart_attendance_data'] = att_data

        # 2. Gender Demographics
        gender_data = list(Member.objects.values('gender').annotate(count=Count('id')))
        g_labels = [x['gender'] or 'Unknown' for x in gender_data]
        g_series = [x['count'] for x in gender_data]
        context['chart_gender_labels'] = g_labels
        context['chart_gender_series'] = g_series

        # 3. Age Group Demographics (Robust Enhancement)
        # Using dob to calculate age groups
        age_bins = {
            '0-12 (Children)': 0,
            '13-19 (Youth)': 0,
            '20-35 (Young Adults)': 0,
            '36-55 (Adults)': 0,
            '56+ (Seniors)': 0,
            'Unknown': 0
        }
        
        all_members = Member.objects.all()
        for m in all_members:
            if m.dob:
                age = (timezone.now().date() - m.dob).days // 365
                if age <= 12: age_bins['0-12 (Children)'] += 1
                elif age <= 19: age_bins['13-19 (Youth)'] += 1
                elif age <= 35: age_bins['20-35 (Young Adults)'] += 1
                elif age <= 55: age_bins['36-55 (Adults)'] += 1
                else: age_bins['56+ (Seniors)'] += 1
            else:
                age_bins['Unknown'] += 1
        
        context['chart_age_labels'] = list(age_bins.keys())
        context['chart_age_series'] = list(age_bins.values())

        # 4. Growth & First-Timers
        # New Members in the period
        context['new_members'] = Member.objects.filter(membership_date__gte=start_date, membership_date__lte=end_date).count()
        # First timers record from Attendance breakdown
        context['total_first_timers'] = Attendance.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(total=Sum('first_timers_count'))['total'] or 0

        # 5. Finance (Filtered)
        inc_monthly = Finance.objects.filter(date__gte=start_date, date__lte=end_date).annotate(
             month=TruncMonth('date')
        ).values('month').annotate(total=Sum('amount')).order_by('month')
        
        exp_monthly = Expense.objects.filter(date__gte=start_date, date__lte=end_date).annotate(
             month=TruncMonth('date')
        ).values('month').annotate(total=Sum('amount')).order_by('month')
        
        fin_labels = []
        fin_income = []
        fin_expense = []
        
        # Helper for finance map
        f_map = {}
        
        curr = start_date.replace(day=1)
        end_curr = end_date.replace(day=1)
        
        iter_date = curr
        while iter_date <= end_curr:
            lbl = iter_date.strftime('%b %Y')
            f_map[lbl] = {'inc':0, 'exp':0}
            fin_labels.append(lbl)
            iter_date = add_month(iter_date)
            
        for x in inc_monthly:
            lbl = x['month'].strftime('%b %Y')
            if lbl in f_map: f_map[lbl]['inc'] = float(x['total'])
            
        for x in exp_monthly:
            lbl = x['month'].strftime('%b %Y')
            if lbl in f_map: f_map[lbl]['exp'] = float(x['total'])
            
        for lbl in fin_labels:
            fin_income.append(f_map[lbl]['inc'])
            fin_expense.append(f_map[lbl]['exp'])

        context['chart_finance_labels'] = fin_labels
        context['chart_finance_income'] = fin_income
        context['chart_finance_expense'] = fin_expense

        return context
