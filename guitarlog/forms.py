from django import forms
from .models import PracticeSong, PracticeSession, PracticeGoal


class PracticeSongForm(forms.ModelForm):
    class Meta:
        model = PracticeSong
        fields = ['title', 'artist', 'difficulty', 'status', 'target_bpm', 'spotify_id', 'album_art_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'}),
            'artist': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'}),
            'target_bpm': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'}),
            'spotify_id': forms.HiddenInput(),
            'album_art_url': forms.HiddenInput(),
        }


class PracticeGoalForm(forms.ModelForm):
    class Meta:
        model = PracticeGoal
        fields = ['weekly_minutes']
        widgets = {
            'weekly_minutes': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2',
                'min': '10',
                'step': '10',
            }),
        }


class QuickRecordForm(forms.ModelForm):
    DURATION_CHOICES = [
        (15, '15分'),
        (30, '30分'),
        (45, '45分'),
        (60, '60分'),
    ]
    duration_minutes = forms.ChoiceField(choices=DURATION_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = PracticeSession
        fields = ['duration_minutes', 'rating', 'memo']
        widgets = {
            'memo': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'}),
        }
