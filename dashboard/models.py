from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


# ──────────────────────────────────────
# Phase 2: Achievement System
# ──────────────────────────────────────

class AchievementDefinition(models.Model):
    CATEGORY_CHOICES = [
        ('practice', '練習'),
        ('live', 'ライブ'),
        ('compose', '作曲'),
        ('general', '全般'),
    ]
    slug = models.SlugField(unique=True)
    name = models.CharField('名前', max_length=100)
    description = models.CharField('説明', max_length=200)
    category = models.CharField('カテゴリ', max_length=20, choices=CATEGORY_CHOICES)
    icon_name = models.CharField('アイコン名', max_length=50)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='achievements',
    )
    achievement = models.ForeignKey(
        AchievementDefinition, on_delete=models.CASCADE,
        related_name='user_achievements',
    )
    earned_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user} - {self.achievement.name}'


# ──────────────────────────────────────
# Phase 3: AI Practice Advice Cache
# ──────────────────────────────────────

class PracticeAdviceCache(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='practice_advice_cache',
    )
    advice_text = models.TextField('アドバイス内容')
    generated_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateField('分析開始日')
    period_end = models.DateField('分析終了日')

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f'{self.user} - {self.generated_at:%Y/%m/%d}'

    def is_stale(self):
        return timezone.now() - self.generated_at > timedelta(hours=24)


# ──────────────────────────────────────
# Phase 6: Push Notifications
# ──────────────────────────────────────

class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    endpoint = models.URLField('エンドポイント', max_length=500, unique=True)
    p256dh = models.CharField('p256dh Key', max_length=200)
    auth = models.CharField('Auth Key', max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.endpoint[:50]}'

    def to_webpush_dict(self):
        return {
            'endpoint': self.endpoint,
            'keys': {'p256dh': self.p256dh, 'auth': self.auth},
        }


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notification_prefs',
    )
    practice_reminder = models.BooleanField('練習リマインダー', default=True)
    live_reminder = models.BooleanField('ライブリマインダー', default=True)
    achievement_notify = models.BooleanField('実績通知', default=True)

    def __str__(self):
        return f'{self.user} の通知設定'
