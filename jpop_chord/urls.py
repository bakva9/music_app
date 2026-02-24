from django.urls import path
from . import views

app_name = 'jpop_chord'

urlpatterns = [
    path('', views.song_list, name='song_list'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('<int:pk>/', views.song_detail, name='song_detail'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
]
