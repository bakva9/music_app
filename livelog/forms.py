from django import forms
from .models import LiveEvent, SetlistEntry, Ticket, Impression, Expense

input_cls = 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'


class LiveEventForm(forms.ModelForm):
    class Meta:
        model = LiveEvent
        fields = ['artist', 'title', 'date', 'venue', 'thumbnail']
        widgets = {
            'artist': forms.TextInput(attrs={'class': input_cls}),
            'title': forms.TextInput(attrs={'class': input_cls}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': input_cls}),
            'venue': forms.TextInput(attrs={'class': input_cls}),
        }


class SetlistEntryForm(forms.ModelForm):
    class Meta:
        model = SetlistEntry
        fields = ['song_title', 'order', 'song_type', 'notes']


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['ticket_type', 'seat_info', 'price']
        widgets = {
            'seat_info': forms.TextInput(attrs={'class': input_cls}),
            'price': forms.NumberInput(attrs={'class': input_cls}),
        }


class ImpressionForm(forms.ModelForm):
    class Meta:
        model = Impression
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5, 'class': input_cls}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'memo', 'date', 'event']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': input_cls}),
            'memo': forms.TextInput(attrs={'class': input_cls}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': input_cls}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['event'].queryset = LiveEvent.objects.filter(user=user)
            self.fields['event'].required = False
