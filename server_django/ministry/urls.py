from django.urls import path
from .views import MinistryListView, MinistryCreateView, MinistryUpdateView, MinistryDeleteView

urlpatterns = [
    path('', MinistryListView.as_view(), name='ministry-list'),
    path('create/', MinistryCreateView.as_view(), name='ministry-create'),
    path('<int:pk>/update/', MinistryUpdateView.as_view(), name='ministry-update'),
    path('<int:pk>/delete/', MinistryDeleteView.as_view(), name='ministry-delete'),
]
