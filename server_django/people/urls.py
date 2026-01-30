from django.urls import path
from .views import MemberListView, MemberStatsView, MemberListCreateView, MemberCreateView, MemberUpdateView, MemberDeleteView, MemberPortalView, mark_attendance, MemberProfileView, MemberFamilyView, MemberEventsView, MemberFinanceView, MemberAnnouncementsView, create_family_group, link_family_member, create_checkout_session

urlpatterns = [
    # Template Views
    path('', MemberListView.as_view(), name='member-list'),
    path('create/', MemberCreateView.as_view(), name='member-create'),
    path('update/<int:pk>/', MemberUpdateView.as_view(), name='member-update'),
    path('delete/<int:pk>/', MemberDeleteView.as_view(), name='member-delete'),
    path('portal/', MemberPortalView.as_view(), name='member-portal'),
    path('portal/profile/', MemberProfileView.as_view(), name='member-profile'),
    path('portal/family/', MemberFamilyView.as_view(), name='member-family'),
    path('portal/events/', MemberEventsView.as_view(), name='member-events'),
    path('portal/contributions/', MemberFinanceView.as_view(), name='member-finance'),
    path('portal/announcements/', MemberAnnouncementsView.as_view(), name='member-announcements'),
    path('api/create-checkout-session/', create_checkout_session, name='create-checkout-session'),
    path('portal/family/create/', create_family_group, name='create-family-group'),
    path('portal/family/link-member/', link_family_member, name='link-family-member'),
    path('mark-attendance/', mark_attendance, name='mark-attendance'),
    
    # API Views (Legacy/Dual-use)
    path('api/list', MemberListCreateView.as_view(), name='api-member-list'),
    path('api/stats', MemberStatsView.as_view(), name='api-member-stats'),
]
