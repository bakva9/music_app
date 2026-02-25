from django.db import models
from django.conf import settings


class Topic(models.Model):
    CATEGORY_CHOICES = [
        ('scale', '音階'),
        ('chord', '和音'),
        ('progression', 'コード進行'),
        ('interval', '音程'),
        ('key', '調'),
        ('rhythm', 'リズム'),
        ('form', '楽曲形式'),
    ]

    DIFFICULTY_CHOICES = [
        (1, '初級'),
        (2, '初中級'),
        (3, '中級'),
        (4, '中上級'),
        (5, '上級'),
    ]

    title = models.CharField('トピック名', max_length=200)
    slug = models.SlugField('スラッグ', unique=True)
    category = models.CharField('カテゴリ', max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.IntegerField('難易度', choices=DIFFICULTY_CHOICES, default=3)
    summary = models.TextField('概要')
    body = models.TextField('本文')
    tags = models.CharField('タグ', max_length=500, blank=True, help_text='カンマ区切りのキーワード')
    related_topics = models.ManyToManyField('self', symmetrical=True, blank=True, verbose_name='関連トピック')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'title']
        verbose_name = '音楽理論トピック'
        verbose_name_plural = '音楽理論トピック'

    def __str__(self):
        return self.title

    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='theory_bookmarks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='bookmarks')
    memo = models.TextField('メモ', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'topic']
        verbose_name = 'ブックマーク'
        verbose_name_plural = 'ブックマーク'

    def __str__(self):
        return f'{self.user} - {self.topic.title}'


class ChordProgression(models.Model):
    STARTING_CHOICES = [
        ('I', 'I 始まり'),
        ('IIm', 'IIm 始まり'),
        ('IIIm', 'IIIm 始まり'),
        ('IV', 'IV 始まり'),
        ('V', 'V 始まり'),
        ('VIm', 'VIm 始まり'),
    ]

    name = models.CharField('進行名', max_length=100)
    slug = models.SlugField('スラッグ', unique=True)
    starting_chord = models.CharField('開始コード', max_length=10, choices=STARTING_CHOICES)
    degrees = models.CharField('ディグリー', max_length=200)
    chords_in_c = models.CharField('Cキーのコード', max_length=200)
    description = models.TextField('説明', blank=True)
    tags = models.CharField('タグ', max_length=500, blank=True)
    order = models.PositiveIntegerField('表示順', default=0)

    class Meta:
        ordering = ['starting_chord', 'order']
        verbose_name = 'コード進行'
        verbose_name_plural = 'コード進行'

    def __str__(self):
        return f'{self.name} ({self.degrees})'

    def chord_list(self):
        return [c.strip() for c in self.chords_in_c.split('→') if c.strip()]
