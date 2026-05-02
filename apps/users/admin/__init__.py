"""
Users admin configuration.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from apps.users.models import UserExtension


class UserExtensionInline(admin.StackedInline):
    model = UserExtension
    can_delete = False
    verbose_name_plural = 'اطلاعات تکمیلی'


class UserAdmin(BaseUserAdmin):
    inlines = (UserExtensionInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserExtension)
class UserExtensionAdmin(admin.ModelAdmin):
    list_display = ['user', 'personnel_code', 'phone_number', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'personnel_code']
    readonly_fields = ['created_at', 'updated_at']
