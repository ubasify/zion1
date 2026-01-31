from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'role_id', 'registration_type', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role_id', 'registration_type', 'ministry', 'parish', 'member')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role_id', 'registration_type', 'ministry', 'parish', 'member')}),
    )

admin.site.register(User, CustomUserAdmin)
