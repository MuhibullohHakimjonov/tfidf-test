from django.urls import path
from django.views.generic import TemplateView

from .views import TFIDFNoDBView

urlpatterns = [
	path('upload/', TFIDFNoDBView.as_view(), name='tfidf-upload'),
]
