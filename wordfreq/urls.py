from django.conf.global_settings import STATIC_URL
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import settings, static

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('tfidf.urls'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
