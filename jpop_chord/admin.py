from django.contrib import admin
from .models import Song, ChordSection, Favorite


class ChordSectionInline(admin.TabularInline):
    model = ChordSection
    extra = 1


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'original_key', 'bpm', 'difficulty')
    list_filter = ('difficulty',)
    search_fields = ('title', 'artist', 'title_kana', 'artist_kana')
    inlines = [ChordSectionInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'capo_setting', 'key_offset', 'created_at')
