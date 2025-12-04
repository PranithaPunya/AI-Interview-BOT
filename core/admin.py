from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    ordering = ("email",)
    search_fields = ("email",)

    # Make username field optional in admin forms
    fieldsets = (
        (None, {"fields": ("email", "password", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.role == CustomUser.ROLE_ADMIN

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.role == CustomUser.ROLE_ADMIN

admin.site.register(CustomUser, CustomUserAdmin)

