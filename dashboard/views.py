from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
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

        context = {
            'bookmark_count': bookmark_count,
            'streak_count': streak_count,
            'live_count': live_count,
            'project_count': project_count,
            'activities': all_activities,
            'practice_week': practice_week,
            'total_minutes': total_minutes,
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
            Q(title__icontains=q) | Q(content__icontains=q)
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
