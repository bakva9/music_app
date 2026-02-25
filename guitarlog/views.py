from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate
from datetime import timedelta
from .models import PracticeSong, PracticeSession, SessionSong, PracticeGoal
from .forms import PracticeSongForm, QuickRecordForm, PracticeGoalForm


@login_required
def home(request):
    streak = PracticeSession.get_streak(request.user)
    recent_sessions = PracticeSession.objects.filter(user=request.user)[:5]
    total_minutes = PracticeSession.objects.filter(user=request.user).aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0

    # 週間目標
    goal = PracticeGoal.objects.filter(user=request.user).first()
    goal_progress = goal.get_progress() if goal else None

    return render(request, 'guitarlog/home.html', {
        'streak': streak,
        'recent_sessions': recent_sessions,
        'total_minutes': total_minutes,
        'goal': goal,
        'goal_progress': goal_progress,
    })


@login_required
def song_list(request):
    status = request.GET.get('status', 'practicing')
    songs = PracticeSong.objects.filter(user=request.user)
    if status != 'all':
        songs = songs.filter(status=status)
    return render(request, 'guitarlog/song_list.html', {
        'songs': songs,
        'current_status': status,
        'status_choices': PracticeSong.STATUS_CHOICES,
    })


@login_required
def song_create(request):
    if request.method == 'POST':
        form = PracticeSongForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)
            song.user = request.user
            song.save()
            return redirect('guitarlog:song_list')
    else:
        form = PracticeSongForm()
    return render(request, 'guitarlog/song_form.html', {'form': form, 'is_edit': False})


@login_required
def song_edit(request, pk):
    song = get_object_or_404(PracticeSong, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PracticeSongForm(request.POST, instance=song)
        if form.is_valid():
            form.save()
            return redirect('guitarlog:song_list')
    else:
        form = PracticeSongForm(instance=song)
    return render(request, 'guitarlog/song_form.html', {'form': form, 'is_edit': True, 'song': song})


@login_required
def song_delete(request, pk):
    song = get_object_or_404(PracticeSong, pk=pk, user=request.user)
    if request.method == 'POST':
        song.delete()
        return redirect('guitarlog:song_list')
    return render(request, 'guitarlog/song_confirm_delete.html', {'song': song})


@login_required
def song_detail(request, pk):
    song = get_object_or_404(PracticeSong, pk=pk, user=request.user)
    entries = (
        SessionSong.objects
        .filter(practice_song=song)
        .select_related('session')
        .order_by('session__started_at')
    )
    # BPM推移データ
    bpm_data = []
    for entry in entries:
        if entry.bpm_achieved:
            bpm_data.append({
                'date': entry.session.started_at.strftime('%m/%d'),
                'bpm': entry.bpm_achieved,
            })
    # 練習統計
    total_time = entries.aggregate(total=Sum('duration_minutes'))['total'] or 0
    avg_bpm = entries.filter(bpm_achieved__isnull=False).aggregate(avg=Avg('bpm_achieved'))['avg']
    session_count = entries.values('session').distinct().count()

    return render(request, 'guitarlog/song_detail.html', {
        'song': song,
        'bpm_data': bpm_data,
        'total_time': total_time,
        'avg_bpm': round(avg_bpm) if avg_bpm else None,
        'session_count': session_count,
    })


@login_required
def timer(request):
    songs = PracticeSong.objects.filter(user=request.user, status='practicing')
    return render(request, 'guitarlog/timer.html', {'songs': songs})


@login_required
def save_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    duration = int(request.POST.get('duration_minutes', 0))
    rating = request.POST.get('rating')
    memo = request.POST.get('memo', '')

    session = PracticeSession.objects.create(
        user=request.user,
        duration_minutes=duration,
        rating=int(rating) if rating else None,
        memo=memo,
    )

    if request.headers.get('HX-Request'):
        return render(request, 'guitarlog/_session_saved.html', {'session': session})
    return redirect('guitarlog:home')


@login_required
def quick_record(request):
    if request.method == 'POST':
        form = QuickRecordForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.is_quick_record = True
            session.save()
            return redirect('guitarlog:home')
    else:
        form = QuickRecordForm()
    return render(request, 'guitarlog/quick_record.html', {'form': form})


@login_required
def set_goal(request):
    goal, created = PracticeGoal.objects.get_or_create(
        user=request.user, defaults={'weekly_minutes': 120}
    )
    if request.method == 'POST':
        form = PracticeGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('guitarlog:home')
    else:
        form = PracticeGoalForm(instance=goal)
    return render(request, 'guitarlog/set_goal.html', {'form': form, 'goal': goal})


@login_required
def stats(request):
    return render(request, 'guitarlog/stats.html')


@login_required
def stats_data(request):
    period = request.GET.get('period', '7')
    try:
        days = int(period)
    except ValueError:
        days = 7
    days = min(max(days, 7), 365)

    today = timezone.now().date()
    start_date = today - timedelta(days=days - 1)
    daily = (
        PracticeSession.objects.filter(
            user=request.user,
            started_at__date__gte=start_date,
        )
        .annotate(date=TruncDate('started_at'))
        .values('date')
        .annotate(total=Sum('duration_minutes'))
        .order_by('date')
    )
    daily_map = {str(d['date']): d['total'] for d in daily}

    labels = []
    data = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        fmt = '%m/%d' if days <= 31 else '%m/%d'
        labels.append(d.strftime(fmt))
        data.append(daily_map.get(str(d), 0))

    total = sum(data)
    avg = round(total / days, 1) if days > 0 else 0

    return JsonResponse({
        'labels': labels,
        'data': data,
        'total': total,
        'avg': avg,
        'days': days,
    })
