from django.urls import path
from .views import EventListView, EventDetailView, EventCreateView, EventUpdateView, EventCalendarView, api_events_feed

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('calendar/', EventCalendarView.as_view(), name='event-calendar'),
    path('create/', EventCreateView.as_view(), name='event-create'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('<int:pk>/update/', EventUpdateView.as_view(), name='event-update'),
    path('api/feed/', api_events_feed, name='api-events-feed'),
]
