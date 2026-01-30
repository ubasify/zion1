from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Ministry

class MinistryListView(LoginRequiredMixin, ListView):
    model = Ministry
    template_name = "ministry/ministry_list.html"
    context_object_name = "ministries"
    paginate_by = 50  # Show more on card view

    def get_queryset(self):
        queryset = super().get_queryset().select_related('parish', 'team_lead').annotate(member_count=Count('member'))
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
            
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate stats for all ministries
        all_ministries = Ministry.objects.annotate(member_count=Count('member'))
        
        # Total volunteers across all ministries
        total_volunteers = sum(m.member_count for m in all_ministries)
        
        # Average report participation (% of times reports were submitted)
        avg_participation = all_ministries.aggregate(avg=Avg('active_participation_rate'))['avg'] or 0
        
        # Reporting compliance (up to date / total)
        up_to_date_count = all_ministries.filter(reporting_status='up_to_date').count()
        total_count = all_ministries.count()
        
        context['stats'] = {
            'total_volunteers': total_volunteers,
            'avg_participation': int(avg_participation),
            'reporting_compliance': f"{up_to_date_count}/{total_count}",
            'up_to_date_count': up_to_date_count,
            'total_count': total_count,
        }
        
        return context


class MinistryCreateView(LoginRequiredMixin, CreateView):
    model = Ministry
    fields = ['name', 'description', 'parish', 'icon_type', 'meeting_day', 'team_lead']
    success_url = reverse_lazy('ministry-list')

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Ministry created successfully',
                'ministry': {
                    'id': self.object.id,
                    'name': self.object.name,
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


class MinistryUpdateView(LoginRequiredMixin, UpdateView):
    model = Ministry
    fields = ['name', 'description', 'parish', 'icon_type', 'active_participation_rate', 'reporting_status', 'last_report_date', 'meeting_day', 'team_lead']
    success_url = reverse_lazy('ministry-list')

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Ministry updated successfully',
                'ministry': {
                    'id': self.object.id,
                    'name': self.object.name,
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


class MinistryDeleteView(LoginRequiredMixin, DeleteView):
    model = Ministry
    success_url = reverse_lazy('ministry-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Ministry deleted successfully'
            })
        return super().delete(request, *args, **kwargs)
