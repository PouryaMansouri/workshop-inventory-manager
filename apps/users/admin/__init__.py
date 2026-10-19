"""
Users admin configuration.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from apps.users.models import UserExtension


class UserExtensionInline(admin.StackedInline):
    model = UserExtension
    can_delete = False
    verbose_name_plural = 'اطلاعات تکمیلی'
    autocomplete_fields = ['user']


class UserCreationFormNoRequiredEmail(UserCreationForm):
    """User creation form with optional email."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].required = False


class UserChangeFormNoRequiredEmail(UserChangeForm):
    """User change form with optional email."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].required = False


class UserAdmin(BaseUserAdmin):
    form = UserChangeFormNoRequiredEmail
    add_form = UserCreationFormNoRequiredEmail
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2')}),
    )
    inlines = (UserExtensionInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'extension__phone_number', 'extension__personnel_code')
    autocomplete_fields = ()


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserExtension)
class UserExtensionAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'personnel_code', 'department']
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone_number',
        'personnel_code',
        'department',
    ]
    autocomplete_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
