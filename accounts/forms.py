from django import forms
from .models import CustomUser, ProfileSettings


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'display_name', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'ユーザー名'}),
            'display_name': forms.TextInput(attrs={'placeholder': '表示名'}),
        }


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = ProfileSettings
        fields = ['is_public', 'show_practice_stats', 'show_live_history',
                  'show_compositions', 'show_achievements', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': '自己紹介を入力...'}),
        }
