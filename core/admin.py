from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (CustomUser,Job, QuestionBank, Candidate, Resume, CandidateJobMapping,
    InterviewSession, GeneratedQuestion, CandidateAnswer, AudioProcessingTask,
    ErrorLog, ActivityLog, AppSettings, Employee)
from django.conf import settings

class CustomUserAdmin(DefaultUserAdmin):
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

# Custom AdminSite-level restriction is possible, but simpler: restrict per ModelAdmin.

class AdminOnlyMixin:
    """
    Mixin to restrict model admin access to users with role == 'admin'.
    """

    def has_module_permission(self, request):
        # Show the app label only to admins
        user = request.user
        return bool(user.is_active and getattr(user, "role", None) == CustomUser.ROLE_ADMIN)

    def has_view_permission(self, request, obj=None):
        user = request.user
        return bool(user.is_active and getattr(user, "role", None) == CustomUser.ROLE_ADMIN)
    def has_add_permission(self, request):
        user = request.user
        return bool(user.is_active and getattr(user, "role", None) == CustomUser.ROLE_ADMIN)

    def has_change_permission(self, request, obj=None):
        user = request.user
        return bool(user.is_active and getattr(user, "role", None) == CustomUser.ROLE_ADMIN)

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return bool(user.is_active and getattr(user, "role", None) == CustomUser.ROLE_ADMIN)
# Register CustomUser with simplified display
#@admin.register(CustomUser)
class CustomUserAdmin(DefaultUserAdmin, AdminOnlyMixin):
    fieldsets = (
        (None, {"fields": ("email", "password", "role")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    list_display = ("email", "role", "is_active", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)

@admin.register(Job)
class JobAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("job_title", "job_code", "experience_level", "created_by", "created_at")
    search_fields = ("job_title", "job_code", "description")
    list_filter = ("experience_level",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(QuestionBank)
class QuestionBankAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("short_text", "job", "category", "difficulty_level")
    search_fields = ("question_text", "job__job_title")
    list_filter = ("category", "difficulty_level")

    def short_text(self, obj):
        return obj.question_text[:75]
    short_text.short_description = "Question"


@admin.register(Candidate)
class CandidateAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "status", "created_at")
    search_fields = ("full_name", "email", "phone")
    list_filter = ("status",)

@admin.register(Resume)
class ResumeAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("candidate", "upload_date")
    search_fields = ("candidate__full_name", "candidate__email")


@admin.register(CandidateJobMapping)
class CandidateJobMappingAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "applied_at")
    search_fields = ("candidate__full_name", "job__job_title")
    list_filter = ("status",)

# Register other models similarly if you want to expose them in admin
admin.site.register(Employee)
admin.site.register(InterviewSession)
admin.site.register(GeneratedQuestion)
admin.site.register(CandidateAnswer)
admin.site.register(AudioProcessingTask)
admin.site.register(ErrorLog)
admin.site.register(ActivityLog)
admin.site.register(AppSettings)