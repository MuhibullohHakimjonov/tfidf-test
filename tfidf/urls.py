from django.urls import path
from .views import (TFIDFMongoUploadView, MetricsView, VersionView, UserDocumentListView, DocumentContentView,
					DocumentStatisticsView, DocumentDeleteView, CollectionListView, CollectionDetailView,
					CollectionStatisticsView, AddDocumentToCollectionView, RemoveDocumentFromCollectionView,
					CollectionCreateView, DeleteCollectionView, DocumentHuffmanView
					)

urlpatterns = [
	path('upload/', TFIDFMongoUploadView.as_view(), name='tfidf-upload'),
	path("metrics/", MetricsView.as_view(), name="metrics"),
	path('version/', VersionView.as_view(), name='version'),

	path('documents/', UserDocumentListView.as_view()),
	path('documents/<int:document_id>/', DocumentContentView.as_view()),
	path('documents/<int:document_id>/huffman/', DocumentHuffmanView.as_view()),
	path('documents/<int:document_id>/statistics/', DocumentStatisticsView.as_view()),
	path('documents/<int:document_id>/delete/', DocumentDeleteView.as_view()),

	path('collections/create/', CollectionCreateView.as_view()),
	path('collections/', CollectionListView.as_view()),
	path('collections/<int:collection_id>/', CollectionDetailView.as_view()),
	path('collections/<int:collection_id>/statistics/', CollectionStatisticsView.as_view()),
	path('collections/<int:collection_id>/<int:document_id>/', AddDocumentToCollectionView.as_view()),
	path('collections/<int:collection_id>/<int:document_id>/delete/', RemoveDocumentFromCollectionView.as_view()),
	path('collections/<int:collection_id>/delete/', DeleteCollectionView.as_view())
]
