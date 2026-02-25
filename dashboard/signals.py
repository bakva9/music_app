from django.db.models.signals import post_save
from django.dispatch import receiver


def _award_if_not_exists(user, slug):
    """Award an achievement if the user doesn't already have it."""
    from .models import AchievementDefinition, UserAchievement
    try:
        defn = AchievementDefinition.objects.get(slug=slug)
    except AchievementDefinition.DoesNotExist:
        return None
    achievement, created = UserAchievement.objects.get_or_create(
        user=user, achievement=defn,
    )
    if created:
        try:
            from .push import send_push_to_user
            send_push_to_user(
                user,
                f'実績解除: {defn.name}',
                defn.description,
                '/achievements/',
            )
        except Exception:
            pass
    return achievement if created else None


def _check_all_rounder(user):
    """Award 'all_rounder' if user has activity in all three areas."""
    from guitarlog.models import PracticeSession
    from livelog.models import LiveEvent
    from songdiary.models import Project

    has_practice = PracticeSession.objects.filter(user=user).exists()
    has_live = LiveEvent.objects.filter(user=user).exists()
    has_compose = Project.objects.filter(user=user).exists()

    if has_practice and has_live and has_compose:
        _award_if_not_exists(user, 'all_rounder')


@receiver(post_save, sender='guitarlog.PracticeSession')
def check_practice_achievements(sender, instance, created, **kwargs):
    if not created:
        return
    user = instance.user
    _award_if_not_exists(user, 'first_practice')

    from guitarlog.models import PracticeSession
    streak = PracticeSession.get_streak(user)
    if streak >= 7:
        _award_if_not_exists(user, 'streak_7')
    if streak >= 30:
        _award_if_not_exists(user, 'streak_30')

    from django.db.models import Sum
    total = PracticeSession.objects.filter(user=user).aggregate(
        t=Sum('duration_minutes'))['t'] or 0
    if total >= 6000:
        _award_if_not_exists(user, 'practice_100h')

    _check_all_rounder(user)


@receiver(post_save, sender='livelog.LiveEvent')
def check_live_achievements(sender, instance, created, **kwargs):
    if not created:
        return
    user = instance.user
    _award_if_not_exists(user, 'first_live')

    from livelog.models import LiveEvent
    if LiveEvent.objects.filter(user=user).count() >= 10:
        _award_if_not_exists(user, 'live_10')

    _check_all_rounder(user)


@receiver(post_save, sender='songdiary.Project')
def check_compose_achievements(sender, instance, created, **kwargs):
    user = instance.user
    if created:
        _award_if_not_exists(user, 'first_compose')
    if instance.status == 'done':
        _award_if_not_exists(user, 'compose_done')
    _check_all_rounder(user)
