from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from datetime import timedelta, date
from itertools import islice
from heapq import merge


def home(request):
    if request.user.is_authenticated:
        from music_theory.models import Bookmark
        from livelog.models import LiveEvent
        from songdiary.models import Project
        from guitarlog.models import PracticeSession
        from django.db.models import Sum
        from django.db.models.functions import TruncDate

        user = request.user

        # --- Stats counts ---
        bookmark_count = Bookmark.objects.filter(user=user).count()
        streak_count = PracticeSession.get_streak(user)
        live_count = LiveEvent.objects.filter(user=user).count()
        project_count = Project.objects.filter(user=user).count()

        # --- Recent activity (latest 8 across all models) ---
        recent_sessions = [
            {'type': 'practice', 'date': s.started_at,
             'text': f'{s.duration_minutes}分練習しました',
             'url': '/practice/'}
            for s in PracticeSession.objects.filter(user=user).order_by('-started_at')[:5]
        ]
        recent_events = [
            {'type': 'live', 'date': e.created_at,
             'text': f'{e.artist} のライブを追加',
             'url': f'/live/{e.pk}/'}
            for e in LiveEvent.objects.filter(user=user).order_by('-created_at')[:5]
        ]
        recent_projects = [
            {'type': 'project', 'date': p.updated_at,
             'text': f'「{p.title}」を更新',
             'url': f'/songs/{p.pk}/'}
            for p in Project.objects.filter(user=user).order_by('-updated_at')[:5]
        ]
        recent_bookmarks = [
            {'type': 'bookmark', 'date': b.created_at,
             'text': f'「{b.topic.title}」をブックマーク',
             'url': f'/theory/{b.topic.slug}/'}
            for b in Bookmark.objects.filter(user=user).select_related('topic').order_by('-created_at')[:5]
        ]

        # Merge and sort by date descending, take top 8
        all_activities = sorted(
            recent_sessions + recent_events + recent_projects + recent_bookmarks,
            key=lambda x: x['date'],
            reverse=True,
        )[:8]

        # --- 7-day practice chart data ---
        today = timezone.now().date()
        start_date = today - timedelta(days=6)
        daily_practice = (
            PracticeSession.objects.filter(user=user, started_at__date__gte=start_date)
            .annotate(date=TruncDate('started_at'))
            .values('date')
            .annotate(total=Sum('duration_minutes'))
        )
        daily_map = {str(d['date']): d['total'] for d in daily_practice}
        practice_week = []
        max_minutes = 1  # avoid division by zero
        for i in range(7):
            d = start_date + timedelta(days=i)
            minutes = daily_map.get(str(d), 0)
            if minutes > max_minutes:
                max_minutes = minutes
            practice_week.append({
                'label': d.strftime('%a'),
                'minutes': minutes,
            })
        # Add percentage for bar height
        for day in practice_week:
            day['pct'] = round(day['minutes'] / max_minutes * 100) if max_minutes > 0 else 0

        total_minutes = PracticeSession.objects.filter(user=user).aggregate(
            total=Sum('duration_minutes'))['total'] or 0

        # Recent achievements
        from .models import UserAchievement
        recent_achievements = (
            UserAchievement.objects.filter(user=user)
            .select_related('achievement')[:6]
        )

        context = {
            'bookmark_count': bookmark_count,
            'streak_count': streak_count,
            'live_count': live_count,
            'project_count': project_count,
            'activities': all_activities,
            'practice_week': practice_week,
            'total_minutes': total_minutes,
            'recent_achievements': recent_achievements,
        }
        return render(request, 'dashboard/home.html', context)
    return render(request, 'dashboard/landing.html')


@login_required
def global_search(request):
    from music_theory.models import Topic
    from livelog.models import LiveEvent
    from songdiary.models import Project
    from guitarlog.models import PracticeSong

    q = request.GET.get('q', '').strip()
    results = {'topics': [], 'songs': [], 'events': [], 'projects': []}

    if q:
        results['topics'] = Topic.objects.filter(
            Q(title__icontains=q) | Q(body__icontains=q)
        )[:10]
        results['songs'] = PracticeSong.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=q) | Q(artist__icontains=q)
        )[:10]
        results['events'] = LiveEvent.objects.filter(
            user=request.user
        ).filter(
            Q(artist__icontains=q) | Q(title__icontains=q) | Q(venue__icontains=q)
        )[:10]
        results['projects'] = Project.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q)
        )[:10]

    total = sum(len(v) for v in results.values())

    return render(request, 'dashboard/search_results.html', {
        'q': q,
        'results': results,
        'total': total,
    })


# ──────────────────────────────────────
# Phase 1: Calendar Heatmap
# ──────────────────────────────────────

@login_required
def calendar_data(request):
    """Return 365-day activity heatmap data as JSON."""
    from guitarlog.models import PracticeSession
    from livelog.models import LiveEvent
    from songdiary.models import Project

    user = request.user
    today = timezone.now().date()
    start = today - timedelta(days=364)

    # Practice: minutes per day
    practice_days = dict(
        PracticeSession.objects.filter(user=user, started_at__date__gte=start)
        .annotate(d=TruncDate('started_at'))
        .values('d')
        .annotate(total=Sum('duration_minutes'))
        .values_list('d', 'total')
    )

    # Live events per day
    live_days = dict(
        LiveEvent.objects.filter(user=user, date__gte=start)
        .values('date')
        .annotate(cnt=Count('id'))
        .values_list('date', 'cnt')
    )

    # Composition updates per day
    compose_days = dict(
        Project.objects.filter(user=user, updated_at__date__gte=start)
        .annotate(d=TruncDate('updated_at'))
        .values('d')
        .annotate(cnt=Count('id'))
        .values_list('d', 'cnt')
    )

    days = []
    active_count = 0
    for i in range(365):
        d = start + timedelta(days=i)
        p = practice_days.get(d, 0)
        l = live_days.get(d, 0)
        c = compose_days.get(d, 0)

        # Activity score: practice minutes weighted + events
        score = min(p // 15, 3) + (l * 2) + c
        level = 0
        if score >= 5:
            level = 4
        elif score >= 3:
            level = 3
        elif score >= 2:
            level = 2
        elif score >= 1:
            level = 1

        if level > 0:
            active_count += 1

        days.append({
            'date': d.isoformat(),
            'level': level,
            'practice': p,
            'live': l,
            'compose': c,
        })

    return JsonResponse({
        'days': days,
        'active_count': active_count,
        'start': start.isoformat(),
    })


@login_required
def calendar_day_detail(request, date_str):
    """Return HTMX partial for a specific day's activities."""
    from guitarlog.models import PracticeSession
    from livelog.models import LiveEvent
    from songdiary.models import Project

    user = request.user
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        return render(request, 'dashboard/_calendar_day.html', {'date': None})

    sessions = PracticeSession.objects.filter(
        user=user, started_at__date=d
    ).order_by('-started_at')

    events = LiveEvent.objects.filter(user=user, date=d)

    projects = Project.objects.filter(
        user=user, updated_at__date=d
    ).order_by('-updated_at')

    return render(request, 'dashboard/_calendar_day.html', {
        'target_date': d,
        'sessions': sessions,
        'events': events,
        'projects': projects,
    })


# ──────────────────────────────────────
# Phase 2: Achievement System
# ──────────────────────────────────────

@login_required
def achievement_list(request):
    """Show all achievements, highlighting earned ones."""
    from .models import AchievementDefinition, UserAchievement

    definitions = AchievementDefinition.objects.all()
    earned_slugs = set(
        UserAchievement.objects.filter(user=request.user)
        .values_list('achievement__slug', flat=True)
    )
    earned_map = {
        ua.achievement.slug: ua
        for ua in UserAchievement.objects.filter(user=request.user).select_related('achievement')
    }

    achievements = []
    for defn in definitions:
        achievements.append({
            'definition': defn,
            'earned': defn.slug in earned_slugs,
            'earned_at': earned_map[defn.slug].earned_at if defn.slug in earned_map else None,
        })

    return render(request, 'dashboard/achievement_list.html', {
        'achievements': achievements,
        'earned_count': len(earned_slugs),
        'total_count': len(definitions),
    })


@login_required
def check_new_achievements(request):
    """Return HTMX partial for unnotified achievements, mark as notified."""
    from .models import UserAchievement

    new_achievements = (
        UserAchievement.objects.filter(user=request.user, notified=False)
        .select_related('achievement')
    )
    achievements_list = list(new_achievements)
    if achievements_list:
        new_achievements.update(notified=True)

    return render(request, 'dashboard/_achievement_toast.html', {
        'new_achievements': achievements_list,
    })


# ──────────────────────────────────────
# Phase 3: AI Practice Advice
# ──────────────────────────────────────

@login_required
def practice_advice(request):
    """Return AI-generated practice advice (HTMX partial)."""
    from .advice import generate_practice_advice

    force = request.GET.get('refresh') == '1'
    if force:
        from .models import PracticeAdviceCache
        PracticeAdviceCache.objects.filter(user=request.user).delete()

    advice_text = generate_practice_advice(request.user)
    return render(request, 'dashboard/_practice_advice.html', {
        'advice_text': advice_text,
    })


# ──────────────────────────────────────
# Phase 4: Spotify Search API
# ──────────────────────────────────────

@login_required
def spotify_search(request):
    """Return Spotify search results as JSON."""
    from .spotify import SpotifyClient

    q = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'track')

    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    client = SpotifyClient()
    if not client.is_available():
        return JsonResponse({'results': []})

    if search_type == 'artist':
        results = client.search_artists(q, limit=5)
    else:
        results = client.search_tracks(q, limit=5)

    return JsonResponse({'results': results})


# ──────────────────────────────────────
# Phase 5: Public Profile
# ──────────────────────────────────────

def public_profile(request, username):
    """Public profile page for a user."""
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    from accounts.models import ProfileSettings
    from guitarlog.models import PracticeSession
    from livelog.models import LiveEvent
    from songdiary.models import Project
    from .models import UserAchievement

    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)

    settings_obj, _ = ProfileSettings.objects.get_or_create(user=profile_user)
    if not settings_obj.is_public:
        return render(request, 'accounts/profile_private.html', status=404)

    context = {
        'profile_user': profile_user,
        'settings': settings_obj,
    }

    if settings_obj.show_practice_stats:
        total_minutes = PracticeSession.objects.filter(user=profile_user).aggregate(
            t=Sum('duration_minutes'))['t'] or 0
        session_count = PracticeSession.objects.filter(user=profile_user).count()
        streak = PracticeSession.get_streak(profile_user)
        context.update({
            'total_minutes': total_minutes,
            'session_count': session_count,
            'streak': streak,
        })

    if settings_obj.show_live_history:
        live_events = LiveEvent.objects.filter(user=profile_user)[:10]
        live_count = LiveEvent.objects.filter(user=profile_user).count()
        context.update({
            'live_events': live_events,
            'live_count': live_count,
        })

    if settings_obj.show_compositions:
        projects = Project.objects.filter(user=profile_user)[:10]
        context['projects'] = projects

    if settings_obj.show_achievements:
        achievements = (
            UserAchievement.objects.filter(user=profile_user)
            .select_related('achievement')
        )
        context['achievements'] = achievements

    return render(request, 'accounts/public_profile.html', context)


@login_required
def profile_settings(request):
    """Profile settings form."""
    from accounts.models import ProfileSettings
    from accounts.forms import ProfileSettingsForm, UserEditForm

    settings_obj, _ = ProfileSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, instance=settings_obj)
        user_form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()
            from django.contrib import messages
            messages.success(request, 'プロフィール設定を更新しました。')
    else:
        form = ProfileSettingsForm(instance=settings_obj)
        user_form = UserEditForm(instance=request.user)

    return render(request, 'accounts/profile_settings.html', {
        'form': form,
        'user_form': user_form,
        'settings': settings_obj,
    })


# ──────────────────────────────────────
# Phase 6: Push Notifications
# ──────────────────────────────────────

@login_required
def push_subscribe(request):
    """Save a push subscription."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    import json
    from .models import PushSubscription

    try:
        data = json.loads(request.body)
        PushSubscription.objects.update_or_create(
            endpoint=data['endpoint'],
            defaults={
                'user': request.user,
                'p256dh': data['keys']['p256dh'],
                'auth': data['keys']['auth'],
            }
        )
        return JsonResponse({'ok': True})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)


@login_required
def push_unsubscribe(request):
    """Remove a push subscription."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    import json
    from .models import PushSubscription

    try:
        data = json.loads(request.body)
        PushSubscription.objects.filter(
            user=request.user, endpoint=data.get('endpoint', '')
        ).delete()
        return JsonResponse({'ok': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data'}, status=400)


def vapid_public_key(request):
    """Return VAPID public key."""
    from django.conf import settings as django_settings
    key = getattr(django_settings, 'VAPID_PUBLIC_KEY', '')
    return JsonResponse({'publicKey': key})


@login_required
def notification_settings(request):
    """Notification preferences form."""
    from .models import NotificationPreference

    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        prefs.practice_reminder = request.POST.get('practice_reminder') == 'on'
        prefs.live_reminder = request.POST.get('live_reminder') == 'on'
        prefs.achievement_notify = request.POST.get('achievement_notify') == 'on'
        prefs.save()
        from django.contrib import messages
        messages.success(request, '通知設定を更新しました。')

    return render(request, 'dashboard/notification_settings.html', {
        'prefs': prefs,
    })
