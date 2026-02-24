from django.contrib import admin
from .models import PracticeSong, PracticeSession, SessionSong


@admin.register(PracticeSong)
class PracticeSongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'user', 'status', 'difficulty')
    list_filter = ('status', 'difficulty')


class SessionSongInline(admin.TabularInline):
    model = SessionSong
    extra = 0


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'started_at', 'duration_minutes', 'rating', 'is_quick_record')
    list_filter = ('is_quick_record',)
    inlines = [SessionSongInline]
