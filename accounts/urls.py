from django.urls import path
from dashboard import views

app_name = 'accounts'

urlpatterns = [
    path('', views.public_profile, name='public_profile'),
]
