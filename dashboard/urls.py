from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.global_search, name='global_search'),
    # Calendar heatmap
    path('calendar/data/', views.calendar_data, name='calendar_data'),
    path('calendar/day/<str:date_str>/', views.calendar_day_detail, name='calendar_day_detail'),
    # Achievements
    path('achievements/', views.achievement_list, name='achievement_list'),
    path('achievements/check/', views.check_new_achievements, name='check_new_achievements'),
    # AI Advice
    path('advice/', views.practice_advice, name='practice_advice'),
    # Spotify
    path('api/spotify/search/', views.spotify_search, name='spotify_search'),
    # Profile settings
    path('settings/profile/', views.profile_settings, name='profile_settings'),
    # Push notifications
    path('push/subscribe/', views.push_subscribe, name='push_subscribe'),
    path('push/unsubscribe/', views.push_unsubscribe, name='push_unsubscribe'),
    path('push/vapid-key/', views.vapid_public_key, name='vapid_public_key'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
]
