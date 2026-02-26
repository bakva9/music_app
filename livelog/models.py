import uuid
from django.db import models
from django.conf import settings


class LiveEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_events')
    share_token = models.UUIDField('共有トークン', default=uuid.uuid4, unique=True, editable=False)
    artist = models.CharField('アーティスト', max_length=200)
    title = models.CharField('公演名', max_length=300, blank=True)
    date = models.DateField('公演日')
    venue = models.CharField('会場', max_length=200, blank=True)
    thumbnail = models.ImageField('サムネイル', upload_to='livelog/thumbnails/', blank=True)
    spotify_artist_id = models.CharField('Spotify Artist ID', max_length=50, blank=True)
    artist_image_url = models.URLField('アーティスト画像', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.artist} ({self.date})'


class SetlistEntry(models.Model):
    SONG_TYPE_CHOICES = [
        ('normal', '通常'),
        ('encore', 'アンコール'),
        ('double_encore', 'ダブルアンコール'),
    ]

    event = models.ForeignKey(LiveEvent, on_delete=models.CASCADE, related_name='setlist')
    song_title = models.CharField('曲名', max_length=200)
    order = models.PositiveIntegerField('順番')
    song_type = models.CharField('種別', max_length=20, choices=SONG_TYPE_CHOICES, default='normal')
    notes = models.CharField('備考', max_length=200, blank=True)

    class Meta:
        ordering = ['event', 'order']

    def __str__(self):
        return f'{self.order}. {self.song_title}'


class Ticket(models.Model):
    TICKET_TYPE_CHOICES = [
        ('standing', 'スタンディング'),
        ('reserved', '指定席'),
        ('arena', 'アリーナ'),
        ('vip', 'VIP'),
        ('other', 'その他'),
    ]

    event = models.OneToOneField(LiveEvent, on_delete=models.CASCADE, related_name='ticket')
    ticket_type = models.CharField('チケット種別', max_length=20, choices=TICKET_TYPE_CHOICES, default='reserved')
    seat_info = models.CharField('座席情報', max_length=100, blank=True)
    price = models.PositiveIntegerField('チケット価格', null=True, blank=True)

    def __str__(self):
        return f'{self.event} - {self.get_ticket_type_display()}'


class Impression(models.Model):
    event = models.OneToOneField(LiveEvent, on_delete=models.CASCADE, related_name='impression')
    text = models.TextField('感想')
    rating = models.IntegerField('評価', choices=[(i, str(i)) for i in range(1, 6)], default=3)

    def __str__(self):
        return f'{self.event} の感想'


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('ticket', 'チケット'),
        ('transport', '交通費'),
        ('goods', 'グッズ'),
        ('food', '飲食'),
        ('accommodation', '宿泊'),
        ('other', 'その他'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_expenses')
    event = models.ForeignKey(LiveEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    amount = models.PositiveIntegerField('金額')
    category = models.CharField('カテゴリ', max_length=20, choices=CATEGORY_CHOICES)
    memo = models.CharField('メモ', max_length=200, blank=True)
    date = models.DateField('日付')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_category_display()} ¥{self.amount:,}'
