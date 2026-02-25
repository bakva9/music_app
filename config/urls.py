from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('sw.js', TemplateView.as_view(
        template_name='sw.js', content_type='application/javascript',
    )),
    path('theory/', include('music_theory.urls')),
    path('practice/', include('guitarlog.urls')),
    path('live/', include('livelog.urls')),
    path('compose/', include('songdiary.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
