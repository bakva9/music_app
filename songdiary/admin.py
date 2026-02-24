from django.contrib import admin
from .models import Project, Memo


class MemoInline(admin.TabularInline):
    model = Memo
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'key', 'bpm', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'tags')
    inlines = [MemoInline]
