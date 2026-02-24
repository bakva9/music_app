from django import forms
from .models import Project

input_cls = 'w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'status', 'key', 'bpm', 'tags', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': input_cls}),
            'key': forms.TextInput(attrs={'class': input_cls, 'placeholder': '例: Cm, G'}),
            'bpm': forms.NumberInput(attrs={'class': input_cls}),
            'tags': forms.TextInput(attrs={'class': input_cls, 'placeholder': 'ロック, バラード'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': input_cls}),
        }
