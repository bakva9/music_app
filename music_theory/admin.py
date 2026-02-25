from django.contrib import admin
from .models import Topic, Bookmark, ChordProgression


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'updated_at')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'tags', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('related_topics',)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'created_at')
    list_filter = ('topic__category',)


@admin.register(ChordProgression)
class ChordProgressionAdmin(admin.ModelAdmin):
    list_display = ('name', 'starting_chord', 'degrees', 'order')
    list_filter = ('starting_chord',)
    search_fields = ('name', 'degrees', 'tags', 'description')
    prepopulated_fields = {'slug': ('name',)}
