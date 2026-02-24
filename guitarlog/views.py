from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from datetime import timedelta
from .models import PracticeSong, PracticeSession, SessionSong
from .forms import PracticeSongForm, QuickRecordForm


@login_required
def home(request):
    streak = PracticeSession.get_streak(request.user)
    recent_sessions = PracticeSession.objects.filter(user=request.user)[:5]
    total_minutes = PracticeSession.objects.filter(user=request.user).aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0
    return render(request, 'guitarlog/home.html', {
        'streak': streak,
        'recent_sessions': recent_sessions,
        'total_minutes': total_minutes,
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
def stats(request):
    return render(request, 'guitarlog/stats.html')


@login_required
def stats_data(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=6)
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
    for i in range(7):
        d = start_date + timedelta(days=i)
        labels.append(d.strftime('%m/%d'))
        data.append(daily_map.get(str(d), 0))
    return JsonResponse({'labels': labels, 'data': data})
