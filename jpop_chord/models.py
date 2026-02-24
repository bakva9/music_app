from django.db import models
from django.conf import settings


class Song(models.Model):
    DIFFICULTY_CHOICES = [
        (1, '初級'),
        (2, '初中級'),
        (3, '中級'),
        (4, '中上級'),
        (5, '上級'),
    ]

    title = models.CharField('曲名', max_length=200)
    title_kana = models.CharField('曲名（かな）', max_length=200, blank=True)
    artist = models.CharField('アーティスト', max_length=200)
    artist_kana = models.CharField('アーティスト（かな）', max_length=200, blank=True)
    original_key = models.CharField('キー', max_length=10, default='C')
    bpm = models.PositiveIntegerField('BPM', null=True, blank=True)
    difficulty = models.IntegerField('難易度', choices=DIFFICULTY_CHOICES, default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['artist', 'title']

    def __str__(self):
        return f'{self.artist} - {self.title}'


class ChordSection(models.Model):
    SECTION_CHOICES = [
        ('intro', 'イントロ'),
        ('verse', 'Aメロ'),
        ('verse2', 'Bメロ'),
        ('chorus', 'サビ'),
        ('bridge', 'Cメロ'),
        ('interlude', '間奏'),
        ('outro', 'アウトロ'),
    ]

    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField('セクション', max_length=20, choices=SECTION_CHOICES)
    order = models.PositiveIntegerField('表示順')
    bar_count = models.PositiveIntegerField('小節数', default=4)
    chords = models.JSONField('コード進行', help_text='例: [["C","","Am",""],["F","G","C",""]]')

    class Meta:
        ordering = ['song', 'order']

    def __str__(self):
        return f'{self.song.title} - {self.get_section_type_display()}'


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='favorites')
    capo_setting = models.IntegerField('カポ位置', default=0)
    key_offset = models.IntegerField('キーオフセット', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'song']

    def __str__(self):
        return f'{self.user} - {self.song.title}'
