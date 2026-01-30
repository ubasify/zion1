from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Event, EventCategory, EventRSVP

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    
    def get_queryset(self):
        queryset = Event.objects.filter(status='published').select_related('category')
        
        # Filter by Category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Search
        query = self.request.GET.get('q')
        if query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
            
        return queryset.order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.objects.all()
        return context

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check user's RSVP status
        if self.request.user.is_authenticated and hasattr(self.request.user, 'member_profile'):
             context['user_rsvp'] = EventRSVP.objects.filter(
                 event=self.object, 
                 member=self.request.user.member_profile
             ).first()
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    template_name = "events/event_form.html"
    fields = ['title', 'description', 'category', 'start_date', 'end_date', 'location', 'is_virtual', 'meeting_link', 'organizer', 'status', 'banner']
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    template_name = "events/event_form.html"
    fields = ['title', 'description', 'category', 'start_date', 'end_date', 'location', 'is_virtual', 'meeting_link', 'organizer', 'status', 'banner']
    success_url = reverse_lazy('event-list')

class EventCalendarView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/event_calendar.html"
    context_object_name = "events"

def api_events_feed(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    events = Event.objects.filter(status='published')
    if start and end:
        events = events.filter(start_date__gte=start, end_date__lte=end)
        
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'url': reverse_lazy('event-detail', args=[event.id]),
            'color': event.category.color if event.category else 'blue',
            # FullCalendar expects specific keys
        })
        
    return JsonResponse(events_data, safe=False)
