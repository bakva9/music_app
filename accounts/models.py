from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    display_name = models.CharField('表示名', max_length=50, blank=True)
    avatar = models.ImageField('アバター', upload_to='avatars/', blank=True)

    def __str__(self):
        return self.display_name or self.username


class ProfileSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile_settings',
    )
    is_public = models.BooleanField('プロフィールを公開', default=False)
    show_practice_stats = models.BooleanField('練習統計を表示', default=True)
    show_live_history = models.BooleanField('ライブ履歴を表示', default=True)
    show_compositions = models.BooleanField('作曲プロジェクトを表示', default=True)
    show_achievements = models.BooleanField('実績を表示', default=True)
    bio = models.TextField('自己紹介', max_length=500, blank=True)

    class Meta:
        verbose_name = 'プロフィール設定'
        verbose_name_plural = 'プロフィール設定'

    def __str__(self):
        return f'{self.user} のプロフィール設定'
