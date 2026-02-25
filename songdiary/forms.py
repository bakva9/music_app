from django import forms
from .models import Project

input_cls = 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'

KEY_CHOICES = [('', '---')] + [
    (k, k) for k in [
        'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B',
        'Cm', 'C#m/Dbm', 'Dm', 'D#m/Ebm', 'Em', 'Fm', 'F#m/Gbm', 'Gm', 'G#m/Abm', 'Am', 'A#m/Bbm', 'Bm',
    ]
]


class ProjectForm(forms.ModelForm):
    key = forms.ChoiceField(
        choices=KEY_CHOICES, required=False, label='キー',
        widget=forms.Select(attrs={'class': input_cls}),
    )

    class Meta:
        model = Project
        fields = ['title', 'status', 'key', 'bpm', 'tags', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': input_cls}),
            'bpm': forms.NumberInput(attrs={'class': input_cls}),
            'tags': forms.TextInput(attrs={'class': input_cls, 'placeholder': 'ロック, バラード'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': input_cls}),
        }
