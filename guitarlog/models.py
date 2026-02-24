from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class PracticeSong(models.Model):
    STATUS_CHOICES = [
        ('practicing', '練習中'),
        ('can_play', '弾ける'),
        ('rest', 'お休み'),
    ]
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_songs')
    title = models.CharField('曲名', max_length=200)
    artist = models.CharField('アーティスト', max_length=200, blank=True)
    difficulty = models.IntegerField('難易度', choices=DIFFICULTY_CHOICES, default=3)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='practicing')
    target_bpm = models.PositiveIntegerField('目標BPM', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'


class PracticeSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_sessions')
    started_at = models.DateTimeField('開始時刻', default=timezone.now)
    ended_at = models.DateTimeField('終了時刻', null=True, blank=True)
    duration_minutes = models.PositiveIntegerField('練習時間（分）', default=0)
    rating = models.IntegerField('評価', choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    memo = models.TextField('メモ', blank=True)
    is_quick_record = models.BooleanField('クイック記録', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} - {self.started_at.strftime("%Y/%m/%d")} ({self.duration_minutes}分)'

    @staticmethod
    def get_streak(user):
        sessions = PracticeSession.objects.filter(user=user).values_list('started_at', flat=True)
        if not sessions:
            return 0
        dates = sorted(set(s.date() for s in sessions), reverse=True)
        today = timezone.now().date()
        if dates[0] < today - timedelta(days=1):
            return 0
        streak = 1
        for i in range(1, len(dates)):
            if dates[i - 1] - dates[i] == timedelta(days=1):
                streak += 1
            else:
                break
        return streak


class SessionSong(models.Model):
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name='session_songs')
    practice_song = models.ForeignKey(PracticeSong, on_delete=models.CASCADE, related_name='session_entries')
    duration_minutes = models.PositiveIntegerField('練習時間（分）', default=0)
    bpm_achieved = models.PositiveIntegerField('達成BPM', null=True, blank=True)

    def __str__(self):
        return f'{self.practice_song.title} - {self.duration_minutes}分'
