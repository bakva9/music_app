from django.shortcuts import render


def home(request):
    if request.user.is_authenticated:
        from music_theory.models import Bookmark
        from livelog.models import LiveEvent
        from songdiary.models import Project
        from guitarlog.models import PracticeSession

        context = {
            'bookmark_count': Bookmark.objects.filter(user=request.user).count(),
            'streak_count': PracticeSession.get_streak(request.user),
            'live_count': LiveEvent.objects.filter(user=request.user).count(),
            'project_count': Project.objects.filter(user=request.user).count(),
        }
        return render(request, 'dashboard/home.html', context)
    return render(request, 'dashboard/landing.html')
