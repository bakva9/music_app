from django.contrib import admin
from .models import Topic, Bookmark, ChordProgression, Conversation, Message


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


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'user__email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')

    def short_content(self, obj):
        return obj.content[:80]
    short_content.short_description = '内容'
