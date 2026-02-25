from django.urls import path
from . import views

app_name = 'songdiary'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/memo/text/', views.add_text_memo, name='add_text_memo'),
    path('<int:pk>/memo/audio/', views.add_audio_memo, name='add_audio_memo'),
    path('<int:pk>/memo/photo/', views.add_photo_memo, name='add_photo_memo'),
    path('<int:pk>/memo/<int:memo_pk>/edit/', views.edit_memo, name='edit_memo'),
    path('<int:pk>/memo/<int:memo_pk>/delete/', views.delete_memo, name='delete_memo'),
]
