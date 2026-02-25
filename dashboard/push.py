import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def send_push_notification(subscription, title, body, url='/'):
    """Send a push notification to a single subscription."""
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning('pywebpush not installed')
        return False

    vapid_private = getattr(settings, 'VAPID_PRIVATE_KEY', '')
    vapid_email = getattr(settings, 'VAPID_ADMIN_EMAIL', '')

    if not vapid_private or not vapid_email:
        return False

    payload = json.dumps({
        'title': title,
        'body': body,
        'url': url,
    })

    try:
        webpush(
            subscription_info=subscription.to_webpush_dict(),
            data=payload,
            vapid_private_key=vapid_private,
            vapid_claims={'sub': f'mailto:{vapid_email}'},
        )
        return True
    except WebPushException as e:
        if e.response and e.response.status_code in (404, 410):
            subscription.delete()
            logger.info(f'Removed stale push subscription: {subscription.endpoint[:50]}')
        else:
            logger.error(f'Push notification error: {e}')
        return False
    except Exception as e:
        logger.error(f'Push notification error: {e}')
        return False


def send_push_to_user(user, title, body, url='/'):
    """Send push notification to all of a user's subscriptions."""
    from .models import PushSubscription, NotificationPreference

    try:
        prefs = NotificationPreference.objects.get(user=user)
        if not prefs.achievement_notify:
            return
    except NotificationPreference.DoesNotExist:
        pass

    subscriptions = PushSubscription.objects.filter(user=user)
    for sub in subscriptions:
        send_push_notification(sub, title, body, url)
