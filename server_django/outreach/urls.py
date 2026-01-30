from django.urls import path
from .views import (
    VisitorListView, VisitorCreateView, VisitorDetailView, 
    FollowUpCreateView, MigrateToMemberView
)

urlpatterns = [
    path('', VisitorListView.as_view(), name='visitor-list'),
    path('new/', VisitorCreateView.as_view(), name='visitor-create'),
    path('<int:pk>/', VisitorDetailView.as_view(), name='visitor-detail'),
    path('<int:pk>/follow-up/', FollowUpCreateView.as_view(), name='followup-create'),
    path('<int:pk>/migrate/', MigrateToMemberView.as_view(), name='visitor-migrate'),
]
