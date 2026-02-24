from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Song, Favorite


def song_list(request):
    songs = Song.objects.all()
    query = request.GET.get('q', '')
    if query:
        songs = songs.filter(
            Q(title__icontains=query) |
            Q(title_kana__icontains=query) |
            Q(artist__icontains=query) |
            Q(artist_kana__icontains=query)
        )
    if request.headers.get('HX-Request'):
        return render(request, 'jpop_chord/_song_search_results.html', {'songs': songs, 'query': query})
    return render(request, 'jpop_chord/song_list.html', {'songs': songs, 'query': query})


def song_detail(request, pk):
    song = get_object_or_404(Song.objects.prefetch_related('sections'), pk=pk)
    is_favorite = False
    favorite = None
    if request.user.is_authenticated:
        try:
            favorite = Favorite.objects.get(user=request.user, song=song)
            is_favorite = True
        except Favorite.DoesNotExist:
            pass
    return render(request, 'jpop_chord/song_detail.html', {
        'song': song,
        'is_favorite': is_favorite,
        'favorite': favorite,
    })


@login_required
def toggle_favorite(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    song = get_object_or_404(Song, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, song=song)
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True
    if request.headers.get('HX-Request'):
        return render(request, 'jpop_chord/_favorite_button.html', {
            'song': song,
            'is_favorite': is_favorite,
        })
    return JsonResponse({'is_favorite': is_favorite})


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('song').order_by('-created_at')
    return render(request, 'jpop_chord/favorite_list.html', {'favorites': favorites})
