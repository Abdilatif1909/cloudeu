from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("LMS profile", {"fields": ("role", "avatar", "phone", "faculty", "direction", "academic_group", "current_semester")}),)
    list_display = ("username", "email", "first_name", "last_name", "role", "academic_group", "is_staff")
    list_filter = ("role", "faculty", "direction", "academic_group", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
