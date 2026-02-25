from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import LiveEvent, SetlistEntry, Ticket, Impression, Expense
from .forms import LiveEventForm, TicketForm, ImpressionForm, ExpenseForm


@login_required
def event_list(request):
    events = LiveEvent.objects.filter(user=request.user)
    upcoming = events.filter(date__gte=timezone.now().date()).order_by('date')
    past = events.filter(date__lt=timezone.now().date())
    return render(request, 'livelog/event_list.html', {
        'upcoming': upcoming,
        'past': past,
    })


@login_required
def event_create(request):
    if request.method == 'POST':
        form = LiveEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('livelog:event_detail', pk=event.pk)
    else:
        form = LiveEventForm()
    return render(request, 'livelog/event_form.html', {'form': form, 'is_edit': False})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(LiveEvent, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LiveEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            ev = form.save(commit=False)
            if request.POST.get('thumbnail-clear'):
                ev.thumbnail = ''
            ev.save()
            return redirect('livelog:event_detail', pk=event.pk)
    else:
        form = LiveEventForm(instance=event)
    return render(request, 'livelog/event_form.html', {'form': form, 'is_edit': True, 'event': event})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(
        LiveEvent.objects.prefetch_related('setlist', 'expenses'),
        pk=pk, user=request.user
    )
    ticket = getattr(event, 'ticket', None)
    impression = getattr(event, 'impression', None)

    # Countdown
    days_until = None
    if event.date >= timezone.now().date():
        days_until = (event.date - timezone.now().date()).days

    return render(request, 'livelog/event_detail.html', {
        'event': event,
        'ticket': ticket,
        'impression': impression,
        'days_until': days_until,
    })


@login_required
def event_delete(request, pk):
    event = get_object_or_404(LiveEvent, pk=pk, user=request.user)
    if request.method == 'POST':
        event.delete()
        return redirect('livelog:event_list')
    return render(request, 'livelog/event_confirm_delete.html', {'event': event})


@login_required
def setlist_add(request, pk):
    event = get_object_or_404(LiveEvent, pk=pk, user=request.user)
    if request.method == 'POST':
        song_title = request.POST.get('song_title', '').strip()
        song_type = request.POST.get('song_type', 'normal')
        notes = request.POST.get('notes', '')
        if song_title:
            order = event.setlist.count() + 1
            SetlistEntry.objects.create(
                event=event, song_title=song_title,
                order=order, song_type=song_type, notes=notes,
            )
    if request.headers.get('HX-Request'):
        return render(request, 'livelog/_setlist.html', {'event': event})
    return redirect('livelog:event_detail', pk=pk)


@login_required
def setlist_delete(request, pk, entry_pk):
    event = get_object_or_404(LiveEvent, pk=pk, user=request.user)
    SetlistEntry.objects.filter(pk=entry_pk, event=event).delete()
    # Reorder
    for i, entry in enumerate(event.setlist.all(), 1):
        if entry.order != i:
            entry.order = i
            entry.save(update_fields=['order'])
    if request.headers.get('HX-Request'):
        return render(request, 'livelog/_setlist.html', {'event': event})
    return redirect('livelog:event_detail', pk=pk)


@login_required
def ticket_edit(request, pk):
    event = get_object_or_404(LiveEvent, pk=pk, user=request.user)
    try:
        ticket = event.ticket
    except Ticket.DoesNotExist:
        ticket = None
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            t = form.save(commit=False)
            t.event = event
            t.save()
            return redirect('livelog:event_detail', pk=pk)
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'livelog/ticket_form.html', {'form': form, 'event': event})


@login_required
def impression_edit(request, pk):
    event = get_object_or_404(LiveEvent, pk=pk, user=request.user)
    try:
        impression = event.impression
    except Impression.DoesNotExist:
        impression = None
    if request.method == 'POST':
        form = ImpressionForm(request.POST, instance=impression)
        if form.is_valid():
            imp = form.save(commit=False)
            imp.event = event
            imp.save()
            return redirect('livelog:event_detail', pk=pk)
    else:
        form = ImpressionForm(instance=impression)
    return render(request, 'livelog/impression_form.html', {'form': form, 'event': event})


@login_required
def live_stats(request):
    from django.db.models import Count
    events = LiveEvent.objects.filter(user=request.user, date__lt=timezone.now().date())

    # アーティスト別ランキング
    artist_ranking = (
        events.values('artist')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # 月別参戦数
    monthly_counts = (
        events.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')[:12]
    )

    # 会場別集計
    venue_ranking = (
        events.exclude(venue='')
        .values('venue')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    total_events = events.count()
    total_artists = events.values('artist').distinct().count()
    total_venues = events.exclude(venue='').values('venue').distinct().count()

    return render(request, 'livelog/live_stats.html', {
        'artist_ranking': artist_ranking,
        'monthly_counts': monthly_counts,
        'venue_ranking': venue_ranking,
        'total_events': total_events,
        'total_artists': total_artists,
        'total_venues': total_venues,
    })


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).select_related('event')
    return render(request, 'livelog/expense_list.html', {'expenses': expenses})


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('livelog:expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'livelog/expense_form.html', {'form': form})


@login_required
def expense_summary(request):
    return render(request, 'livelog/expense_summary.html')


@login_required
def expense_summary_data(request):
    monthly = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')[:6]
    )
    by_category = (
        Expense.objects.filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = dict(Expense.CATEGORY_CHOICES)
    return JsonResponse({
        'monthly': [{'month': m['month'].strftime('%Y/%m'), 'total': m['total']} for m in monthly],
        'by_category': [{'category': category_labels.get(c['category'], c['category']), 'total': c['total']} for c in by_category],
    })
