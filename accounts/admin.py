from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'display_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('追加情報', {'fields': ('display_name',)}),
    )
