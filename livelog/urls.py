from django.urls import path
from . import views

app_name = 'livelog'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('<int:pk>/setlist/add/', views.setlist_add, name='setlist_add'),
    path('<int:pk>/setlist/<int:entry_pk>/delete/', views.setlist_delete, name='setlist_delete'),
    path('<int:pk>/ticket/', views.ticket_edit, name='ticket_edit'),
    path('<int:pk>/impression/', views.impression_edit, name='impression_edit'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/summary/', views.expense_summary, name='expense_summary'),
    path('expenses/summary/data/', views.expense_summary_data, name='expense_summary_data'),
]
