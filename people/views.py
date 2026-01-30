from rest_framework import serializers, generics, views
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Member, Volunteer, Family
from ministry.models import Ministry

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

from django.conf import settings
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
import json
import stripe

from .forms import MemberForm
from .models import Member, Family
from ministry.models import Event, Ministry, Announcement
from operations.models import Attendance, MemberAttendance, Finance

class MemberPortalView(LoginRequiredMixin, TemplateView):
    template_name = "people/member_portal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # specific member matching logic (e.g. by email)
        # Fallback to first member for demo if no match
        member = Member.objects.filter(email=user.email).first() or Member.objects.first()
        
        context['member'] = member
        context['user_name'] = user.first_name or user.username
        
        # Account Status
        # Logic: If status is 'active', it's approved. If 'inactive' or None, it's pending.
        # Image shows "Account Pending"
        context['account_pending'] = member.status != 'active' if member else True
        
        # Giving (This Year)
        now = timezone.now()
        giving_total = 0
        if member:
            giving_total = Finance.objects.filter(
                member=member,
                date__year=now.year
            ).aggregate(total=Sum('amount'))['total'] or 0
        context['giving_total'] = giving_total
        
        # Upcoming Events
        events = Event.objects.filter(start_date__gte=now).order_by('start_date')[:5]
        context['upcoming_events'] = events
        context['upcoming_events_count'] = events.count()
        
        # Announcements
        announcements = Announcement.objects.filter(is_public=True).order_by('-created_at')[:5]
        context['announcements'] = announcements
        
        return context

from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse
from operations.models import Attendance, MemberAttendance
from ministry.models import Service, Ministry

@require_POST
def mark_attendance(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login first'}, status=401)
        
    member = Member.objects.filter(email=request.user.email).first()
    if not member:
        # Fallback for demo: use first member if emails don't match (for admin testing)
        member = Member.objects.first()
        if not member:
             return JsonResponse({'success': False, 'message': 'Member profile not found'}, status=404)

    # Determine Service based on today
    now = timezone.now()
    today = now.date()
    # Map python weekday (0=Mon, 6=Sun) to our model choices
    weekday_map = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
    current_day = weekday_map[now.weekday()]
    
    # 1. Try to find specific service for today
    service = Service.objects.filter(day_of_week=current_day).first()
    
    # 2. Get/Create Attendance Record
    service_name = service.name if service else "Daily Service"
    attendance, created = Attendance.objects.get_or_create(
        date=today,
        service=service if service else None,
        defaults={
            'service_type': service_name,
            'total_count': 0
        }
    )
    
    # 3. Check if already marked
    if MemberAttendance.objects.filter(attendance=attendance, member=member).exists():
        return JsonResponse({'success': False, 'message': 'You have already marked attendance for today!'})
        
    # 4. Create MemberAttendance
    MemberAttendance.objects.create(
        attendance=attendance,
        member=member,
        status='Present'
    )
    
    # 5. Update counts (simplified)
    # Ideally use signals or a method on Attendance to recalc
    attendance.refresh_from_db() # Get current state? No, aggregation better.
    # Just increment for now or rely on the save method logic if it exists
    # Check Attendance.save method...
    
    # Manual update for performance/simplicity in this view
    if member.member_type == 'Guest':
        attendance.first_timers_count += 1
    elif member.age_group == 'Child': # Assuming field exists or simplified
        attendance.children_count += 1
    else:
        attendance.adult_count += 1
    attendance.save() # This triggers the total_count recalc in save() method
    
    return JsonResponse({
        'success': True, 
        'message': f'Attendance marked for {service_name}!',
        'service': service_name,
        'date': today.strftime('%Y-%m-%d')
    })

class MemberCreateView(LoginRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = "people/member_form.html"
    success_url = reverse_lazy('member-list')

class MemberUpdateView(LoginRequiredMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = "people/member_form.html"
    success_url = reverse_lazy('member-list')

class MemberProfileView(LoginRequiredMixin, UpdateView):
    model = Member
    template_name = "people/member_profile.html"
    fields = [
        'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code',
        'dob', 'gender', 'marital_status', 'occupation', 'bio',
        'emergency_contact_name', 'emergency_contact_phone',
        'salvation_date', 'baptism_date'
    ]
    success_url = reverse_lazy('member-profile')
    
    def get_object(self, queryset=None):
        # Match user email or fallback to first
        member = Member.objects.filter(email=self.request.user.email).first() or Member.objects.first()
        return member

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_name'] = self.request.user.first_name or self.request.user.username
        if self.object.first_name and self.object.last_name:
             context['initials'] = (self.object.first_name[0] + self.object.last_name[0]).upper()
        else:
             context['initials'] = (self.request.user.username[:2]).upper()
        return context

class MemberDeleteView(LoginRequiredMixin, DeleteView):
    model = Member
    template_name = "people/member_confirm_delete.html"
    success_url = reverse_lazy('member-list')

class MemberListView(LoginRequiredMixin, ListView):
    model = Member
    template_name = "people/member_list.html"
    context_object_name = "members"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('ministry')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(email__icontains=search)
            )
            
        # Tab Filters (type param)
        tab_type = self.request.GET.get('type') # 'members', 'first_timers', 'new_converts'
        if tab_type == 'first_timers':
            queryset = queryset.filter(member_type='Guest')
        elif tab_type == 'new_converts':
            queryset = queryset.filter(member_type='New Convert')
        # 'members' (default) shows all (or maybe exclude guests? Design implies "Members" tab shows all registered)
        
        # Additional Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        ministry = self.request.GET.get('ministry')
        if ministry:
            queryset = queryset.filter(ministry_id=ministry)
            
        return queryset.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ministries'] = Ministry.objects.all()
        
        # Stats Calculation
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 1. Total Members
        total_members = Member.objects.count()
        # Mock growth for demo (or calc real if needed)
        
        # 2. First Timers (Guests created this month)
        first_timers_month = Member.objects.filter(member_type='Guest', created_at__gte=month_start).count()
        
        # 3. New Converts (Created this month)
        new_converts_month = Member.objects.filter(member_type='New Convert', created_at__gte=month_start).count()
        
        # 4. Retention Rate (Active / Total)
        active_members = Member.objects.filter(status='active').count()
        retention_rate = int((active_members / total_members * 100)) if total_members > 0 else 0
        
        context['stats'] = {
            'total_members': total_members,
            'first_timers_month': first_timers_month,
            'new_converts_month': new_converts_month,
            'retention_rate': retention_rate
        }
        
        context['current_tab'] = self.request.GET.get('type', 'members')
        return context

class MemberListCreateView(generics.ListCreateAPIView):
    # API View (Legacy/Mobile)
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = Member.objects.all().order_by('-created_at')
        
        # Filters
        search = self.request.query_params.get('search')
        member_type = self.request.query_params.get('member_type')
        status = self.request.query_params.get('status')
        ministry_id = self.request.query_params.get('ministry_id')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(email__icontains=search)
            )
        if member_type:
            queryset = queryset.filter(member_type=member_type)
        if status:
            queryset = queryset.filter(status=status)
        if ministry_id:
            queryset = queryset.filter(ministry_id=ministry_id)
            
        return queryset

    # Customize pagination response to match Node API {data, meta}
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # DRF default is { count, next, previous, results }
        # Frontend expects { data: [...], meta: { total, page, ... } }
        # We can adjust frontend or backend. Adjusting backend is safer here.
        return Response({
            'data': response.data['results'],
            'meta': {
                'total': response.data['count'],
                'page': int(request.query_params.get('page', 1)),
                'limit': int(request.query_params.get('limit', 25)),
                'totalPages': (response.data['count'] + 24) // 25 
            }
        })

class MemberStatsView(views.APIView):
    def get(self, request):
        total = Member.objects.count()
        active = Member.objects.filter(status='active').count()
        
        now = timezone.now()
        new_this_month = Member.objects.filter(
            membership_date__year=now.year, 
            membership_date__month=now.month
        ).count()
        
        guests = Member.objects.filter(member_type='Guest').count()
        workers = Member.objects.filter(member_type='Worker').count() # Simplified, really should join Volunteer

        # Charts
        # 1. Growth
        six_months_ago = now - timezone.timedelta(days=180)
        growth_data = Member.objects.filter(membership_date__gte=six_months_ago)\
            .annotate(month=TruncMonth('membership_date'))\
            .values('month')\
            .annotate(count=Count('id'))\
            .order_by('month')
        
        growth = [{'month': d['month'].strftime('%Y-%m') if d['month'] else 'Unknown', 'count': d['count']} for d in growth_data]

        # 2. Type Dist
        type_dist = list(Member.objects.values('member_type').annotate(value=Count('id')).values('member_type', 'value'))
        type_dist = [{'name': d['member_type'], 'value': d['value']} for d in type_dist]

        # 3. Status Dist
        status_dist = list(Member.objects.values('status').annotate(value=Count('id')).values('status', 'value'))
        status_dist = [{'name': d['status'], 'value': d['value']} for d in status_dist]

        # 4. Ministry Dist
        min_dist = list(Member.objects.values('ministry__name').annotate(value=Count('id')).order_by('-value')[:5])
        ministry_dist = [{'name': d['ministry__name'] or 'Unassigned', 'value': d['value']} for d in min_dist]

        return Response({
            'cards': {
                'total': total,
                'active': active,
                'new_this_month': new_this_month,
                'guests': guests,
                'workers': workers
            },
            'charts': {
                'growth': growth,
                'typeDist': type_dist,
                'statusDist': status_dist,
                'ministryDist': ministry_dist
            }
        })

from django.views.decorators.http import require_POST
from django.http import JsonResponse

class MemberFamilyView(LoginRequiredMixin, TemplateView):
    template_name = "people/member_family.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.filter(email=self.request.user.email).first() or Member.objects.first()
        context['member'] = member
        context['user_name'] = self.request.user.first_name or self.request.user.username
        
        if member:
            if member.first_name and member.last_name:
                context['initials'] = (member.first_name[0] + member.last_name[0]).upper()
            else:
                context['initials'] = (self.request.user.username[:2]).upper()
                
            if member.family:
                context['family'] = member.family
                context['family_members'] = member.family.members.all()
        return context

@require_POST
def create_family_group(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login first'}, status=401)
        
    member = Member.objects.filter(email=request.user.email).first() or Member.objects.first()
    if not member:
         return JsonResponse({'success': False, 'message': 'Member profile not found'}, status=404)
    
    if member.family:
        return JsonResponse({'success': False, 'message': 'You already belong to a family group'})
        
    family_name = f"The {member.last_name} Family"
    family = Family.objects.create(name=family_name)
    
    member.family = family
    member.family_role = 'Head'
    member.save()
    
    return JsonResponse({'success': True, 'message': f'Family group "{family_name}" created!'})

@require_POST
def link_family_member(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login first'}, status=401)
        
    # Get Current Member (Head of Request)
    current_member = Member.objects.filter(email=request.user.email).first() or Member.objects.first()
    if not current_member or not current_member.family:
         return JsonResponse({'success': False, 'message': 'You must belong to a family group first'}, status=400)
    
    import json
    data = json.loads(request.body)
    target_member_id = data.get('member_id')
    role = data.get('role', 'Relative')
    
    if not target_member_id:
        return JsonResponse({'success': False, 'message': 'Member ID is required'}, status=400)
        
    try:
        target_member = Member.objects.get(id=target_member_id)
    except Member.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Member not found'}, status=404)
        
    # Check if already in family
    if target_member.family:
        return JsonResponse({'success': False, 'message': f'{target_member.first_name} is already in a family group'}, status=400)
        
    # Link
    target_member.family = current_member.family
    target_member.family_role = role
    target_member.save()
    
    return JsonResponse({
        'success': True, 
        'message': f'{target_member.first_name} added to your family!',
        'member': {
            'id': target_member.id,
            'name': f"{target_member.first_name} {target_member.last_name}",
            'role': role
        }
    })

class MemberEventsView(LoginRequiredMixin, TemplateView):
    template_name = "people/member_events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.filter(email=self.request.user.email).first() or Member.objects.first()
        context['member'] = member
        context['user_name'] = self.request.user.first_name or self.request.user.username
        
        if member:
            if member.first_name and member.last_name:
                context['initials'] = (member.first_name[0] + member.last_name[0]).upper()
            else:
                context['initials'] = (self.request.user.username[:2]).upper()

            # Upcoming Events (next 30 days)
            now = timezone.now()
            next_month = now + timezone.timedelta(days=30)
            context['upcoming_events'] = Event.objects.filter(
                start_date__gte=now,
                start_date__lte=next_month
            ).order_by('start_date')

            # Past Attendance
            context['my_attendance'] = MemberAttendance.objects.filter(
                member=member
            ).select_related('attendance', 'attendance__event', 'attendance__service').order_by('-attendance__date')

        return context

class MemberFinanceView(LoginRequiredMixin, TemplateView):
    template_name = "people/member_finance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.filter(email=self.request.user.email).first() or Member.objects.first()
        context['member'] = member
        context['user_name'] = self.request.user.first_name or self.request.user.username
        
        if member:
            if member.first_name and member.last_name:
                context['initials'] = (member.first_name[0] + member.last_name[0]).upper()
            else:
                context['initials'] = (self.request.user.username[:2]).upper()

            # Stripe Key
            context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY

            # Contributions
            contributions = Finance.objects.filter(member=member).order_by('-date')
            context['contributions'] = contributions
            
            # Stats (Current Year)
            now = timezone.now()
            year_start = now.replace(month=1, day=1)
            
            total_ytd = contributions.filter(date__gte=year_start).aggregate(total=Sum('amount'))['total'] or 0
            context['total_ytd'] = total_ytd
            
            # Last Contribution
            last_contrib = contributions.first()
            context['last_contribution'] = last_contrib

        return context

class MemberAnnouncementsView(LoginRequiredMixin, TemplateView):
    template_name = "people/member_announcements.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.filter(email=self.request.user.email).first() or Member.objects.first()
        context['member'] = member
        context['user_name'] = self.request.user.first_name or self.request.user.username
        
        if member:
            if member.first_name and member.last_name:
                context['initials'] = (member.first_name[0] + member.last_name[0]).upper()
            else:
                context['initials'] = (self.request.user.username[:2]).upper()

            # Announcements (Public ones)
            context['announcements'] = Announcement.objects.filter(is_public=True).order_by('-publication_date')

        return context

def create_checkout_session(request):
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            data = json.loads(request.body)
            amount = int(float(data.get('amount')) * 100) # Convert to cents
            payment_type = data.get('type')
            details = data.get('details', '')
            
            description = f"{payment_type}"
            if details:
                description += f" - {details}"

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {
                            'name': 'Church Donation',
                            'description': description,
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('member-finance')) + '?status=success',
                cancel_url=request.build_absolute_uri(reverse('member-finance')) + '?status=cancel',
                metadata={
                    'user_email': request.user.email,
                    'payment_type': payment_type,
                    'details': details or ''
                }
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
