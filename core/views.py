from django.views.generic import TemplateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework import serializers, generics, permissions, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from operations.models import Attendance, Finance, CommunityImpact, Expense
from people.models import Member
from ministry.models import Ministry, Parish, SmallGroup
from events.models import Event
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from .models import UserLoginLog
import json

User = get_user_model()

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role_id == 1

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

class AdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    template_name = "core/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_users': User.objects.count(),
            'total_parishes': Parish.objects.count(),
            'total_ministries': Ministry.objects.count(),
            'total_members': Member.objects.count(),
            'recent_users': User.objects.select_related('member', 'parish').order_by('-date_joined')[:5],
            'recent_members': Member.objects.order_by('-created_at')[:5],
        })
        return context

class AdminUserListView(SuperAdminRequiredMixin, ListView):
    model = User
    template_name = "core/admin/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('member', 'parish', 'ministry').order_by('-date_joined')

class AdminParishListView(SuperAdminRequiredMixin, ListView):
    model = Parish
    template_name = "core/admin/parish_list.html"
    context_object_name = "parishes"

class AdminMinistryListView(SuperAdminRequiredMixin, ListView):
    model = Ministry
    template_name = "core/admin/ministry_list.html"
    context_object_name = "ministries"

class AdminAuditLogView(SuperAdminRequiredMixin, ListView):
    model = UserLoginLog
    template_name = "core/admin/audit_logs.html"
    context_object_name = "logs"
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        
        # Filters
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        ip_addr = self.request.GET.get('ip')
        if ip_addr:
            queryset = queryset.filter(ip_address__icontains=ip_addr)
            
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(login_datetime__date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(login_datetime__date__lte=date_to)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('username')
        return context

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role_id', 'ministry', 'parish')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role_id=validated_data.get('role_id', 4)
        )
        return user

from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm

class RegisterView(CreateView):
    template_name = 'core/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from operations.models import Attendance
from people.models import Member
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Sum
import json

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from operations.models import Attendance, Finance
from people.models import Member
from ministry.models import Ministry
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Sum, Count, Q
import json

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from operations.models import Attendance, Finance, CommunityImpact, Expense
from people.models import Member
from ministry.models import Ministry, SmallGroup
from events.models import Event
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
import json

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        week_start = today - timedelta(days=today.weekday()) # Monday
        
        last_att_date = None
        
        # --- Top Cards ---
        
        # Date Filters
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        filter_start = None
        filter_end = None

        if start_date_str and end_date_str:
            try:
                filter_start = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                filter_end = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # --- Top Cards ---
        
        # 1. Total Attendance
        # If filtered, sum usage in range. Else, last Sunday.
        if filter_start and filter_end:
            total_attendance = Attendance.objects.filter(date__range=[filter_start, filter_end])\
                .aggregate(sum=Sum('total_count'))['sum'] or 0
        else:
            # Last recorded Sunday
            last_att_record = Attendance.objects.order_by('-date').first()
            last_att_date = last_att_record.date if last_att_record else None
            total_attendance = 0
            if last_att_date:
                total_attendance = Attendance.objects.filter(date=last_att_date).aggregate(sum=Sum('total_count'))['sum'] or 0

        # ... (other cards logic simplified, omitting for brevity based on instruction to add filtering)
        # Actually I need to keep the other cards logic intact or wrap it.
        # Let's assume we filter Filter-able metrics (Attendance, Giving) but keep "New Visitors" relative to the view.
        
        # Avg this month (or Avg in Range if filtered)
        if filter_start and filter_end:
             # Avg per entry in range
             month_avg = Attendance.objects.filter(date__range=[filter_start, filter_end])\
                .aggregate(avg=Avg('total_count'))['avg'] or 0
        else:
            month_avg = Attendance.objects.filter(date__year=now.year, date__month=now.month)\
                .values('date').annotate(day_total=Sum('total_count'))\
                .aggregate(avg=Avg('day_total'))['avg'] or 0

        # 2. New Visitors (This Week)
        if filter_start and filter_end:
            new_visitors = Attendance.objects.filter(date__range=[filter_start, filter_end])\
                .aggregate(sum=Sum('first_timers_count'))['sum'] or 0
        else:
            new_visitors = Attendance.objects.filter(date__gte=week_start).aggregate(sum=Sum('first_timers_count'))['sum'] or 0
        
        # 3. Weekly Giving
        if filter_start and filter_end:
            weekly_giving = Finance.objects.filter(date__range=[filter_start, filter_end])\
                .aggregate(sum=Sum('amount'))['sum'] or 0
            # Goal is hard to define for range, let's just show raw total. 
            # Or assume goal accumulates: 50k * weeks.
            # Keeping simple: just show total, percentage might be irrelevant or >100%
            giving_percentage = 0 # Hide percentage for custom range or calc differently?
            # Let's try to scale goal:
            weeks = max(1, int((filter_end - filter_start).days / 7))
            weekly_goal = 50000 * weeks
            giving_percentage = int((weekly_giving / weekly_goal) * 100) if weekly_goal > 0 else 0
        else:
            # This week's total
            weekly_giving = Finance.objects.filter(date__gte=week_start).aggregate(sum=Sum('amount'))['sum'] or 0
            weekly_goal = 50000 
            giving_percentage = int((weekly_giving / weekly_goal) * 100) if weekly_goal > 0 else 0

        # 5. Retention Rate (Active Members / Total Members)
        total_mems = Member.objects.count()
        active_mems = Member.objects.filter(status='active').count()
        # Fallback to avoid division by zero
        retention_rate = int((active_mems / total_mems) * 100) if total_mems > 0 else 0

        # 6. Community Impact (Total People Reached)
        if filter_start and filter_end:
            total_impact = CommunityImpact.objects.filter(date__range=[filter_start, filter_end])\
                .aggregate(sum=Sum('people_impacted'))['sum'] or 0
        else:
            total_impact = CommunityImpact.objects.aggregate(sum=Sum('people_impacted'))['sum'] or 0

        # ...
        
        # 5. Attendance Trends
        # If filtered, show data in that range. Else Default logic.
        
        # 5. Attendance Trends
        # Always show Jan-Dec comparison for the selected year (or current year) vs Previous Year
        
        chart_year = filter_start.year if filter_start else now.year
        prev_year = chart_year - 1

        # Helper to get monthly totals
        def get_monthly_data(year):
            data = Attendance.objects.filter(date__year=year)\
                .values('date__month').annotate(total=Sum('total_count')).order_by('date__month')
            monthly_totals = [0] * 12
            for entry in data:
                # date__month is 1-12, index is 0-11
                monthly_totals[entry['date__month'] - 1] = entry['total']
            return monthly_totals

        this_year_total = get_monthly_data(chart_year)
        last_year_total = get_monthly_data(prev_year)
        
        trend_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # We pass THIS YEAR (or selected year) as main data, LAST YEAR as comparison
        chart_data_payload = {
            'labels': trend_labels,
            'this_year': this_year_total,
            'last_year': last_year_total
        }

        # 6. Weekly Service Summary (Breakdown of last Sunday)
        service_summary = []
        # 6. Weekly Service Summary (Last 7 Days from end of range/current date)
        
        # Determine the "anchor date" for the summary
        anchor_date = filter_end if filter_end else now.date()
        
        # Find the start of that week (or just last 7 days). 
        # Requirement: "Weekly Service Tables". Let's show the services belonging to the week ending on anchor_date.
        # Actually, let's just grab the last 7 days ending on anchor_date or latest recorded date.
        
        last_att_record = Attendance.objects.order_by('-date').first()
        latest_db_date = last_att_record.date if last_att_record else now.date()
        
        ref_date = filter_end if (filter_end and filter_end <= latest_db_date) else latest_db_date
        week_window_start = ref_date - timedelta(days=6)
        
        recent_services = Attendance.objects.filter(date__range=[week_window_start, ref_date])
        
        # Static Metadata Map
        service_meta = {
            "Evening Sacrifice": {"medium": "Online(Zoom)/Physical", "day": "Monday", "time": "6:00pm"},
            "Marriage Counselling": {"medium": "Online (YouTube)", "day": "Wednesday", "time": "7:30pm"},
            "Blast Service": {"medium": "Physical (Church Hall)", "day": "Thursday", "time": "6:30pm"},
            "Evangelism": {"medium": "Physical (Church Hall)", "day": "Saturday", "time": "2:00pm"},
            "Sunday Service": {"medium": "Online/Physical", "day": "Sunday", "time": "9:00am"},
            # Fallbacks
            "9:00 AM Classic": {"medium": "Physical", "day": "Sunday", "time": "9:00am"},
            "11:00 AM Modern": {"medium": "Physical", "day": "Sunday", "time": "11:00am"},
        }
        
        service_summary = []
        for svc in recent_services:
            meta = service_meta.get(svc.service_type, {"medium": "Physical", "day": svc.date.strftime('%A'), "time": "TBD"})
            
            # Mock capacity
            capacity = 1000
            percent = int((svc.total_count / capacity) * 100)
            
            service_summary.append({
                'name': svc.service_type,
                'count': svc.total_count,
                'percent': percent,
                'medium': meta['medium'],
                'day': meta['day'],
                'time': meta['time']
            })
            
        # Sort by Day-of-week logic? Or Date? Sorting by Date is safest.
        # But 'recent_services' is unsorted?
        recent_services = recent_services.order_by('date')
        
        # Re-build sorted list
        service_summary = []
        for svc in recent_services:
            meta = service_meta.get(svc.service_type, {"medium": "Physical", "day": svc.date.strftime('%A'), "time": "TBD"})
            capacity = 1000
            percent = int((svc.total_count / capacity) * 100)
             
            service_summary.append({
                'name': svc.service_type,
                'count': svc.total_count,
                'percent': percent,
                'medium': meta['medium'],
                'day': meta['day'],
                'time': meta['time']
            })

        # --- Row 3: Giving Trend & Activity ---
        
        # 1. Giving Trend (Jan-Dec for selected year)
        # Using chart_year from Attendance logic
        
        # 1. Giving Trend (Jan-Dec for selected year vs Previous Year)
        # Using chart_year from Attendance logic (defined above as filter_year or current_year)
        
        def get_monthly_giving(year):
            data = Finance.objects.filter(date__year=year)\
                .annotate(month=TruncMonth('date'))\
                .values('month').annotate(total=Sum('amount')).order_by('month')
            totals = [0] * 12
            for entry in data:
                totals[entry['month'].month - 1] = float(entry['total'])
            return totals

        giving_this_year = get_monthly_giving(chart_year)
        giving_last_year = get_monthly_giving(prev_year)
        
        giving_payload = {
            'this_year': giving_this_year,
            'last_year': giving_last_year,
            'years': [chart_year, prev_year]
        }
            
        # 2. Expense Trend (Jan-Dec for selected year vs Previous Year)
        # Mirroring Giving logic
        def get_monthly_expense(year):
            data = Expense.objects.filter(date__year=year)\
                .annotate(month=TruncMonth('date'))\
                .values('month').annotate(total=Sum('amount')).order_by('month')
            totals = [0] * 12
            for entry in data:
                totals[entry['month'].month - 1] = float(entry['total'])
            return totals

        expense_this_year = get_monthly_expense(chart_year)
        expense_last_year = get_monthly_expense(prev_year)

        expense_payload = {
            'this_year': expense_this_year,
            'last_year': expense_last_year,
            'years': [chart_year, prev_year]
        }

        # 3. Recent Activity (Dynamic based on filter)
        # If filter set: use range. Else: last 30 days or so? User said "current period" if no date.
        # "Current period" usually means "This Month" or "Last 30 Days". Let's default to Last 30 Days.
        
        if filter_start and filter_end:
            act_start, act_end = filter_start, filter_end
        else:
            act_end = now.date()
            act_start = act_end - timedelta(days=30)
            
        # Fetch Top ~5-10 items from Finance, Attendance, Expense
        recent_finance = Finance.objects.filter(date__range=[act_start, act_end]).order_by('-date')[:5]
        recent_expenses = Expense.objects.filter(date__range=[act_start, act_end]).order_by('-date')[:5]
        recent_attendance = Attendance.objects.filter(date__range=[act_start, act_end]).order_by('-date')[:5]
        
        activity_stream = []
        for f in recent_finance:
            activity_stream.append({
                'type': 'finance',
                'date': f.date,
                'title': f'{f.category} Received',
                'desc': f'Amount: ${f.amount:,.2f}',
                'icon': 'banknote',
                'color': 'green'
            })
            
        for e in recent_expenses:
             activity_stream.append({
                'type': 'expense',
                'date': e.date,
                'title': f'Expense: {e.category}',
                'desc': f'Amount: ${e.amount:,.2f}',
                'icon': 'credit-card',
                'color': 'red'
            })

        for a in recent_attendance:
            activity_stream.append({
                'type': 'attendance',
                'date': a.date,
                'title': f'{a.service_type}',
                'desc': f'Attendance: {a.total_count}',
                'icon': 'users',
                'color': 'blue'
            })
            
        # Community Impact in Activity Stream
        recent_impacts = CommunityImpact.objects.filter(date__range=[act_start, act_end]).order_by('-date')[:5]
        for i in recent_impacts:
            activity_stream.append({
                'type': 'impact',
                'date': i.date,
                'title': i.name,
                'desc': f'Reached: {i.people_impacted}',
                'icon': 'heart',
                'color': 'teal'
            })
        # Sort combined stream by date desc
        activity_stream.sort(key=lambda x: x['date'], reverse=True)
        activity_stream = activity_stream[:10] # increased limit

        # --- Bottom Row ---

        # 7. Top Parish Returns (Replacement for Active Ministries)
        # Identify the parish with the highest returns in the selected period (or year)
        
        # Determine range (same as chart_year logic earlier)
        # Using giving_this_year/chart_year logic implicitly
        
        # 7. Top Parishes List (For new "Parish Performance" Card)
        # Fetch Top 5 Parishes by Returns in current year
        
        top_parishes_qs = Finance.objects.filter(date__year=chart_year, parish__isnull=False)\
            .values('parish__id', 'parish__name', 'parish__address')\
            .annotate(total_returns=Sum('amount'))\
            .order_by('-total_returns')[:5]
            
        parish_list = []
        for p in top_parishes_qs:
            p_id = p['parish__id']
            curr_returns = p['total_returns']
            
            # Returns Growth
            prev_returns = Finance.objects.filter(date__year=prev_year, parish_id=p_id)\
                .aggregate(total=Sum('amount'))['total'] or 0
                
            returns_growth = 0
            if prev_returns > 0:
                returns_growth = int(((curr_returns - prev_returns) / prev_returns) * 100)
            elif curr_returns > 0:
                returns_growth = 100
            
            # Members Growth (Cumulative up to end of year)
            # Current Members: Joined on or before Dec 31 of chart_year
            curr_members = Member.objects.filter(created_at__year__lte=chart_year, parish_id=p_id).count()
            
            # Prev Members: Joined on or before Dec 31 of prev_year
            prev_members = Member.objects.filter(created_at__year__lte=prev_year, parish_id=p_id).count()
            
            members_growth = 0
            if prev_members > 0:
                members_growth = int(((curr_members - prev_members) / prev_members) * 100)
            elif curr_members > 0:
                members_growth = 100

            parish_list.append({
                'name': p['parish__name'],
                'location': p['parish__address'] or 'Main Campus',
                'returns': curr_returns,
                'returns_growth': returns_growth,
                'members': curr_members,
                'members_growth': members_growth,
            })

        context.update({
            'cards': {
                'total_attendance': int(total_attendance),
                'month_avg': int(month_avg),
                'new_visitors': new_visitors,
                'weekly_giving': int(weekly_giving) if weekly_giving else 0,
                'giving_percentage': giving_percentage,
                'retention_rate': retention_rate,
                'total_members': Member.objects.count(),
                'total_impact': total_impact,
            },
            'parish_list': parish_list,
            # 'health_score': health_score, # Deprecated
            'chart_data': json.dumps(chart_data_payload),
            'giving_chart_data': json.dumps(giving_payload),
            'expense_chart_data': json.dumps(expense_payload),
            'activity_stream': activity_stream,
            'upcoming_events': Event.objects.filter(status='published', start_date__gte=now).order_by('start_date')[:5],
            'chart_year': chart_year,
        })
        
        return context
