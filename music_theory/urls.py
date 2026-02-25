from django.urls import path
from . import views

app_name = 'music_theory'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('progressions/', views.progression_list, name='progression_list'),
    path('diatonic/', views.diatonic_reference, name='diatonic_reference'),
    path('<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
]
