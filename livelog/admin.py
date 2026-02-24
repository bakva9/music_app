from django.contrib import admin
from .models import LiveEvent, SetlistEntry, Ticket, Impression, Expense


class SetlistInline(admin.TabularInline):
    model = SetlistEntry
    extra = 1


class TicketInline(admin.StackedInline):
    model = Ticket
    extra = 0


class ImpressionInline(admin.StackedInline):
    model = Impression
    extra = 0


@admin.register(LiveEvent)
class LiveEventAdmin(admin.ModelAdmin):
    list_display = ('artist', 'title', 'date', 'venue', 'user')
    list_filter = ('date',)
    search_fields = ('artist', 'title', 'venue')
    inlines = [SetlistInline, TicketInline, ImpressionInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'event')
    list_filter = ('category', 'date')
