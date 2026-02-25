from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Topic, Bookmark, ChordProgression


def topic_list(request):
    topics = Topic.objects.all()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if query:
        topics = topics.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__icontains=query) |
            Q(body__icontains=query)
        )
    if category:
        topics = topics.filter(category=category)

    context = {
        'topics': topics,
        'query': query,
        'current_category': category,
        'categories': Topic.CATEGORY_CHOICES,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'music_theory/_topic_search_results.html', context)
    return render(request, 'music_theory/topic_list.html', context)


def topic_detail(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, topic=topic).exists()
    return render(request, 'music_theory/topic_detail.html', {
        'topic': topic,
        'is_bookmarked': is_bookmarked,
        'related_topics': topic.related_topics.all(),
    })


@login_required
def toggle_bookmark(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    topic = get_object_or_404(Topic, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, topic=topic)
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True
    if request.headers.get('HX-Request'):
        return render(request, 'music_theory/_bookmark_button.html', {
            'topic': topic,
            'is_bookmarked': is_bookmarked,
        })
    return JsonResponse({'is_bookmarked': is_bookmarked})


@login_required
def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('topic').order_by('-created_at')
    return render(request, 'music_theory/bookmark_list.html', {'bookmarks': bookmarks})


def progression_list(request):
    progressions = ChordProgression.objects.all()
    starting = request.GET.get('starting', '')
    if starting:
        progressions = progressions.filter(starting_chord=starting)
    context = {
        'progressions': progressions,
        'current_starting': starting,
        'starting_choices': ChordProgression.STARTING_CHOICES,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'music_theory/_progression_results.html', context)
    return render(request, 'music_theory/progression_list.html', context)


def diatonic_reference(request):
    return render(request, 'music_theory/diatonic_reference.html')
