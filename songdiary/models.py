from django.db import models
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = [
        ('idea', 'アイデア'),
        ('sketch', 'スケッチ'),
        ('composing', '作曲中'),
        ('arranging', '編曲中'),
        ('lyrics', '作詞中'),
        ('recording', 'レコーディング'),
        ('done', '完成'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compose_projects')
    title = models.CharField('タイトル', max_length=200)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='idea')
    key = models.CharField('キー', max_length=10, blank=True)
    bpm = models.PositiveIntegerField('BPM', null=True, blank=True)
    tags = models.CharField('タグ', max_length=200, blank=True, help_text='カンマ区切り')
    description = models.TextField('概要', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Memo(models.Model):
    MEMO_TYPE_CHOICES = [
        ('text', 'テキスト'),
        ('audio', '音声'),
        ('photo', '写真'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memos')
    memo_type = models.CharField('種類', max_length=10, choices=MEMO_TYPE_CHOICES, default='text')
    text_content = models.TextField('テキスト', blank=True)
    audio_file = models.FileField('音声ファイル', upload_to='songdiary/audio/', blank=True)
    photo_file = models.ImageField('写真', upload_to='songdiary/photos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_memo_type_display()} - {self.created_at.strftime("%Y/%m/%d %H:%M")}'
