from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from datetime import datetime
from rest_framework import status, permissions
from bson import ObjectId
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Document, Collection
from .mongo import get_documents_collection, get_mongo_collections
from .serializers import CollectionSerializer, DocumentSerializer, CollectionCreateSerializer, TFIDFUploadSerializer, \
	DocumentStatisticsSerializer, CollectionStatisticsSerializer



class TFIDFMongoUploadView(APIView):
	parser_classes = [MultiPartParser]
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		serializer = TFIDFUploadSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			result = serializer.save()
			return Response({
				"message": "Files processed and stored successfully in MongoDB",
				**result
			}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MetricsView(APIView):
	def get(self, request):
		try:
			collections = get_mongo_collections()
			documents = list(collections["documents_collection"].find({}))

			if not documents:
				return Response({"message": "No data available"}, status=status.HTTP_204_NO_CONTENT)

			word_counts = [d.get("word_count", 0) for d in documents]
			file_sizes = [d.get("file_size", 0) for d in documents]
			timestamps = [
				datetime.fromisoformat(d["uploaded_at"]) for d in documents if "uploaded_at" in d
			]

			metrics = {
				"files_processed": len(documents),
				"avg_file_size": round(sum(file_sizes) / len(file_sizes), 3) if file_sizes else 0,
				"total_words_processed": sum(word_counts),
				"avg_words_per_file": round(sum(word_counts) / len(word_counts), 3) if word_counts else 0,
				"latest_file_processed_timestamp": round(max(timestamps).timestamp(), 3) if timestamps else None,
			}

			return Response(metrics, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"error": f"Error retrieving metrics: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VersionView(APIView):
	def get(self, request):
		return Response({'version': '2.0'}, status=status.HTTP_200_OK)


class UserDocumentListView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		paginator = PageNumberPagination()
		paginator.page_size = 20
		queryset = Document.objects.filter(user=request.user)
		result_page = paginator.paginate_queryset(queryset, request)
		serializer = DocumentSerializer(result_page, many=True)
		return paginator.get_paginated_response(serializer.data)


class DocumentContentView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, document_id):
		doc = get_object_or_404(Document, id=document_id, user=request.user)
		mongo_doc = get_documents_collection().find_one({"_id": ObjectId(doc.mongo_id)})
		if not mongo_doc:
			raise Http404("Document not found in MongoDB")
		return Response({"content": mongo_doc.get("content", "")})


class DocumentStatisticsView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, document_id):
		doc = get_object_or_404(Document, id=document_id, user=request.user)
		mongo_doc = get_documents_collection().find_one({"_id": ObjectId(doc.mongo_id)})
		if not mongo_doc:
			raise Http404("Statistics not found")

		mongo_doc["tfidf_data"] = mongo_doc.get("tfidf_data", [])[:50]

		serializer = DocumentStatisticsSerializer(
			mongo_doc,
			context={"document": doc}
		)
		return Response(serializer.data)


class DocumentDeleteView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def delete(self, request, document_id):
		doc = get_object_or_404(Document, id=document_id, user=request.user)
		get_documents_collection().delete_one({"_id": ObjectId(doc.mongo_id)})
		doc.delete()
		return Response({"message": "Document deleted"})


class CollectionCreateView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = CollectionCreateSerializer

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid():
			name = serializer.validated_data['name']
			collection = Collection.objects.create(user=request.user, name=name)
			return Response({"id": collection.id, "name": collection.name}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionListView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		paginator = PageNumberPagination()
		paginator.page_size = 20
		collections = Collection.objects.filter(user=request.user)
		result_page = paginator.paginate_queryset(collections, request)
		serializer = CollectionSerializer(result_page, many=True)
		return paginator.get_paginated_response(serializer.data)


class CollectionDetailView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, collection_id):
		collection = get_object_or_404(Collection, id=collection_id, user=request.user)
		serializer = CollectionSerializer(collection)
		return Response({"collections_id": serializer.data})


class CollectionStatisticsView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, collection_id):
		collection = get_object_or_404(Collection, id=collection_id, user=request.user)
		try:
			serializer = CollectionStatisticsSerializer.from_collection(collection)
			return Response(serializer.data)
		except ValidationError as ve:
			return Response({"error": str(ve)}, status=404)
		except Exception as e:
			return Response({"error": f"Failed to compute statistics: {e}"}, status=500)


class AddDocumentToCollectionView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, collection_id, document_id):
		collection = get_object_or_404(Collection, id=collection_id, user=request.user)
		document = get_object_or_404(Document, id=document_id, user=request.user)
		collection.documents.add(document)
		return Response({"message": "Document added to collection"})


class RemoveDocumentFromCollectionView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def delete(self, request, collection_id, document_id):
		collection = get_object_or_404(Collection, id=collection_id, user=request.user)
		document = get_object_or_404(Document, id=document_id, user=request.user)
		collection.documents.remove(document)
		return Response({"message": "Document removed from collection"})


class DeleteCollectionView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def delete(self, request, collection_id):
		collection = get_object_or_404(Collection, id=collection_id, user=request.user)
		collection.delete()
		return Response({"message": "Document deleted"})
