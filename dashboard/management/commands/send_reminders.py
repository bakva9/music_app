from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Send push notification reminders (streak protection, live reminders)'

    def handle(self, *args, **options):
        self._check_streak_reminders()
        self._check_live_reminders()

    def _check_streak_reminders(self):
        """Notify users who practiced yesterday but not today."""
        from guitarlog.models import PracticeSession
        from dashboard.models import NotificationPreference
        from dashboard.push import send_push_to_user

        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        users_practiced_yesterday = (
            PracticeSession.objects.filter(started_at__date=yesterday)
            .values_list('user_id', flat=True).distinct()
        )
        users_practiced_today = set(
            PracticeSession.objects.filter(started_at__date=today)
            .values_list('user_id', flat=True).distinct()
        )

        for user_id in users_practiced_yesterday:
            if user_id in users_practiced_today:
                continue

            try:
                prefs = NotificationPreference.objects.get(user_id=user_id)
                if not prefs.practice_reminder:
                    continue
            except NotificationPreference.DoesNotExist:
                pass

            user = User.objects.get(pk=user_id)
            send_push_to_user(
                user,
                'ストリークを守ろう！',
                '昨日も練習してましたね。今日も少しだけ弾いてストリークを維持しましょう。',
                '/practice/',
            )
            self.stdout.write(f'  Sent streak reminder to {user.username}')

    def _check_live_reminders(self):
        """Notify users who have a live event tomorrow."""
        from livelog.models import LiveEvent
        from dashboard.models import NotificationPreference
        from dashboard.push import send_push_to_user

        tomorrow = timezone.now().date() + timedelta(days=1)
        events = LiveEvent.objects.filter(date=tomorrow).select_related('user')

        for event in events:
            try:
                prefs = NotificationPreference.objects.get(user=event.user)
                if not prefs.live_reminder:
                    continue
            except NotificationPreference.DoesNotExist:
                pass

            send_push_to_user(
                event.user,
                '明日はライブ！',
                f'{event.artist} のライブが明日です。楽しんできてください！',
                f'/live/{event.pk}/',
            )
            self.stdout.write(f'  Sent live reminder to {event.user.username} for {event.artist}')
