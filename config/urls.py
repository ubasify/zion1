from django.contrib import admin
from django.urls import path, include
from core.views import (
    DashboardView, AdminDashboardView, AdminUserListView,
    AdminParishListView, AdminMinistryListView, AdminAuditLogView
)
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('auth/', include('core.urls')),
    
    # Admin Panel (Root Access)
    path('admin-panel/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin-panel/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin-panel/parishes/', AdminParishListView.as_view(), name='admin-parish-list'),
    path('admin-panel/ministries/', AdminMinistryListView.as_view(), name='admin-ministry-list'),
    path('admin-panel/audit-logs/', AdminAuditLogView.as_view(), name='admin-audit-logs'),

    path('people/', include('people.urls')),
    path('events/', include('events.urls')),
    path('analytics/', include('analytics.urls')),
    path('ministries/', include('ministry.urls')),
    path('attendance/', include('operations.urls')),
    path('outreach/', include('outreach.urls')),
    path('employees/', include('employees.urls')),
    path('finance/analytics/', RedirectView.as_view(url='/analytics/', permanent=True)),
    path('finance/', include('operations.urls')),
]
