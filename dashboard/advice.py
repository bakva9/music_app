import logging
from datetime import timedelta

from django.conf import settings
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone

logger = logging.getLogger(__name__)

ADVICE_SYSTEM_PROMPT = """あなたは「残音」アプリの練習コーチです。ユーザーの直近の練習データを分析し、パーソナライズされたアドバイスを提供してください。

## ルール
- 日本語で回答すること
- 簡潔に（200文字以内で）
- 3つのセクションに分けて回答:
  1. 📊 今週のサマリー（1-2行）
  2. 💪 良かった点（1つ）
  3. 🎯 今週のアドバイス（具体的な提案1つ）
- データがない場合は「まだデータが少ないので、練習を始めましょう！」のように励ます
- ポジティブなトーンを保つ
- 音楽以外の話題には触れない
"""


def gather_practice_context(user, days=7):
    """Gather practice data for the last N days."""
    from guitarlog.models import PracticeSession, PracticeSong
    from livelog.models import LiveEvent
    from songdiary.models import Project

    today = timezone.now().date()
    start = today - timedelta(days=days - 1)

    sessions = PracticeSession.objects.filter(
        user=user, started_at__date__gte=start
    )

    total_minutes = sessions.aggregate(t=Sum('duration_minutes'))['t'] or 0
    session_count = sessions.count()

    # Daily breakdown
    daily = list(
        sessions.annotate(d=TruncDate('started_at'))
        .values('d')
        .annotate(total=Sum('duration_minutes'))
        .order_by('d')
    )

    # Streak
    streak = PracticeSession.get_streak(user)

    # Songs practiced
    songs = list(
        PracticeSong.objects.filter(user=user, status='practicing')
        .values('title', 'artist', 'target_bpm')[:5]
    )

    # Recent live events
    live_count = LiveEvent.objects.filter(
        user=user, date__gte=start
    ).count()

    # Composition activity
    compose_count = Project.objects.filter(
        user=user, updated_at__date__gte=start
    ).count()

    return {
        'total_minutes': total_minutes,
        'session_count': session_count,
        'daily': daily,
        'streak': streak,
        'songs': songs,
        'live_count': live_count,
        'compose_count': compose_count,
        'days': days,
    }


def format_advice_prompt(ctx):
    """Format gathered data into a Gemini prompt."""
    parts = [f'【直近{ctx["days"]}日間の練習データ】']
    parts.append(f'・練習回数: {ctx["session_count"]}回')
    parts.append(f'・合計時間: {ctx["total_minutes"]}分')
    parts.append(f'・連続練習日数（ストリーク）: {ctx["streak"]}日')

    if ctx['daily']:
        days_str = ', '.join(
            f'{d["d"].strftime("%m/%d")}={d["total"]}分' for d in ctx['daily']
        )
        parts.append(f'・日別: {days_str}')

    if ctx['songs']:
        songs_str = ', '.join(
            f'{s["title"]}({s["artist"]})' for s in ctx['songs']
        )
        parts.append(f'・練習中の曲: {songs_str}')

    if ctx['live_count']:
        parts.append(f'・ライブ参戦: {ctx["live_count"]}回')
    if ctx['compose_count']:
        parts.append(f'・作曲活動: {ctx["compose_count"]}件')

    parts.append('\nこのデータを分析して、練習アドバイスをください。')
    return '\n'.join(parts)


def generate_practice_advice(user):
    """Generate or return cached practice advice."""
    from .models import PracticeAdviceCache

    # Check cache
    latest = PracticeAdviceCache.objects.filter(user=user).first()
    if latest and not latest.is_stale():
        return latest.advice_text

    # Gather context
    ctx = gather_practice_context(user, days=7)

    # Call Gemini
    try:
        import google.generativeai as genai
    except ImportError:
        return 'アドバイス機能は現在利用できません。'

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return 'アドバイス機能は設定中です。'

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',
            system_instruction=ADVICE_SYSTEM_PROMPT,
        )
        response = model.generate_content(format_advice_prompt(ctx))
        advice_text = response.text

        # Cache
        today = timezone.now().date()
        PracticeAdviceCache.objects.create(
            user=user,
            advice_text=advice_text,
            period_start=today - timedelta(days=6),
            period_end=today,
        )
        # Clean old cache entries
        PracticeAdviceCache.objects.filter(user=user).order_by('-generated_at')[5:].delete()

        return advice_text

    except Exception as e:
        logger.error(f'Practice advice generation error: {e}')
        if latest:
            return latest.advice_text
        return '練習を続けて、データが貯まるとアドバイスが表示されます。'
