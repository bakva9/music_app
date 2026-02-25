from django.contrib import admin
from .models import (
    AchievementDefinition, UserAchievement,
    PracticeAdviceCache, PushSubscription, NotificationPreference,
)


@admin.register(AchievementDefinition)
class AchievementDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'sort_order']
    list_filter = ['category']
    ordering = ['sort_order']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at', 'notified']
    list_filter = ['achievement', 'notified']
    raw_id_fields = ['user']


@admin.register(PracticeAdviceCache)
class PracticeAdviceCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'generated_at', 'period_start', 'period_end']
    raw_id_fields = ['user']


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    raw_id_fields = ['user']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'practice_reminder', 'live_reminder', 'achievement_notify']
    raw_id_fields = ['user']
