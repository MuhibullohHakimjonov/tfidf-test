from django.urls import path
from .views import TFIDFMongoUploadView, MetricsView, VersionView

urlpatterns = [
	path('upload/', TFIDFMongoUploadView.as_view(), name='tfidf-upload'),
	path("metrics/", MetricsView.as_view(), name="metrics"),
	path('version/', VersionView.as_view(), name='version')

]
