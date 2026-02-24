from django.urls import path
from . import views

app_name = 'guitarlog'

urlpatterns = [
    path('', views.home, name='home'),
    path('songs/', views.song_list, name='song_list'),
    path('songs/create/', views.song_create, name='song_create'),
    path('songs/<int:pk>/edit/', views.song_edit, name='song_edit'),
    path('songs/<int:pk>/delete/', views.song_delete, name='song_delete'),
    path('timer/', views.timer, name='timer'),
    path('save-session/', views.save_session, name='save_session'),
    path('quick/', views.quick_record, name='quick_record'),
    path('stats/', views.stats, name='stats'),
    path('stats/data/', views.stats_data, name='stats_data'),
]
