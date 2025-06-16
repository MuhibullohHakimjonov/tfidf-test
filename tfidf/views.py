from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework import status, permissions
from bson import ObjectId
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Document, Collection
from .mongo import get_documents_collection, get_metrics_collection, update_collection_statistics_in_mongo
from .serializers import CollectionSerializer, DocumentSerializer, CollectionCreateSerializer, TFIDFUploadSerializer, \
	DocumentStatisticsSerializer, CollectionStatisticsSerializer
from .utils import build_huffman_tree, generate_codes, huffman_encode, compute_global_tfidf_table


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
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		try:
			metrics_collection = get_metrics_collection()

			if request.user.is_superuser or request.user.is_staff:
				metrics = metrics_collection.find_one({"_id": "global_metrics"})

				if not metrics:
					return Response({"message": "No global metrics available."}, status=status.HTTP_204_NO_CONTENT)

				total_batches = metrics.get("total_batches_uploaded", 0)
				avg_time = round(metrics.get("sum_time_processed", 0.0) / total_batches,
								 3) if total_batches > 0 else 0.0

				response_data = {
					"files_processed": metrics.get("total_files_uploaded", 0),
					"min_time_processed": round(metrics.get("min_time_processed", 0.0), 3),
					"avg_time_processed": avg_time,
					"max_time_processed": round(metrics.get("max_time_processed", 0.0), 3),
					"latest_file_processed_timestamp": round(metrics.get("latest_file_processed_timestamp", 0.0), 3)
				}
			else:
				user_files = Document.objects.filter(user=request.user)
				files_count = user_files.count()

				if files_count == 0:
					return Response({"message": "No user metrics available."}, status=status.HTTP_204_NO_CONTENT)

				sizes = list(user_files.values_list('size', flat=True))
				word_counts = list(user_files.values_list('word_count', flat=True))

				response_data = {
					"files_processed": files_count,
					"min_file_size": min(sizes),
					"avg_file_size": round(sum(sizes) / files_count, 3),
					"max_file_size": max(sizes),
					"min_word_count": min(word_counts),
					"avg_word_count": round(sum(word_counts) / files_count, 3),
					"max_word_count": max(word_counts),
				}

			return Response(response_data, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VersionView(APIView):
	def get(self, request):
		return Response({'version': '3.0'}, status=status.HTTP_200_OK)


class DocumentHuffmanView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, document_id):
		doc = Document.objects.filter(id=document_id, user=request.user).first()
		if not doc:
			raise Http404("Document not found")

		mongo_doc = get_documents_collection().find_one({"_id": ObjectId(doc.mongo_id)})
		if not mongo_doc:
			raise Http404("Document content not found in MongoDB")

		content = mongo_doc.get("content", "")
		if not content:
			return JsonResponse({"error": "Document content is empty"}, status=400)

		tree = build_huffman_tree(content)
		code_map = generate_codes(tree)
		encoded_text = huffman_encode(content, code_map)

		# пагинация
		offset = int(request.GET.get('offset', 0))
		limit = int(request.GET.get('limit', 10000))
		total_size = len(encoded_text)
		end = offset + limit
		paginated_text = encoded_text[offset:end]
		is_end = end >= total_size

		return JsonResponse({
			"huffman_codes": code_map,
			"encoded_text": paginated_text,
			"total_size": total_size,
			"offset": offset,
			"limit": limit,
			"is_end": is_end
		}, json_dumps_params={'ensure_ascii': False})


class UserDocumentListView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		paginator = PageNumberPagination()
		paginator.page_size = 20
		queryset = Document.objects.filter(user=request.user).order_by('-id')
		result_page = paginator.paginate_queryset(queryset, request)
		serializer = DocumentSerializer(result_page, many=True)
		return paginator.get_paginated_response(serializer.data)


class DocumentContentView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, document_id):
		doc = get_object_or_404(Document, id=document_id, user=request.user)
		mongo_doc = get_documents_collection().find_one(
			{"_id": ObjectId(doc.mongo_id)}, {"content": 1}
		)
		if not mongo_doc:
			raise Http404("Document not found in MongoDB")

		content = mongo_doc.get("content", "")
		offset = int(request.query_params.get("offset", 0))
		limit = int(request.query_params.get("limit", 10000))

		sliced_content = content[offset:offset + limit]

		return Response({
			"content": sliced_content,
			"total_size": len(content),
			"offset": offset,
			"limit": limit,
			"is_end": offset + limit >= len(content)
		})


class DocumentStatisticsView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, document_id):
		doc = get_object_or_404(Document, id=document_id, user=request.user)
		collection_id = request.query_params.get('collection_id')
		page = int(request.query_params.get('page', 1))
		page_size = int(request.query_params.get('page_size', 50))
		if collection_id:
			collection = get_object_or_404(Collection, id=collection_id, user=request.user)
			mongo_ids = [d.mongo_id for d in collection.documents.all()]
			documents = list(get_documents_collection().find({
				"_id": {"$in": [ObjectId(mongo_id) for mongo_id in mongo_ids]}
			}))

			if not documents:
				raise Http404("No documents found in MongoDB for this collection")

			texts = [doc.get("content", "") for doc in documents]
			tfidf_results, _ = compute_global_tfidf_table(texts)

			tf_aggregated = {}
			for d in tfidf_results:
				for entry in d:
					word = entry["word"]
					tf_aggregated[word] = tf_aggregated.get(word, 0) + entry["tf"]

			idf_lookup = {entry["word"]: entry["idf"] for entry in tfidf_results[0]}

			tfidf_combined = [
				{"word": word, "total_tf": round(tf, 6), "idf": round(idf_lookup[word], 6)}
				for word, tf in tf_aggregated.items()
			]

			tfidf_data = sorted(tfidf_combined, key=lambda x: x["idf"], reverse=True)

		else:
			# Статистика только по документу
			mongo_doc = get_documents_collection().find_one({"_id": ObjectId(doc.mongo_id)})
			if not mongo_doc:
				raise Http404("Statistics not found for the document")

			tfidf_data = mongo_doc.get("tfidf_data", [])
		start = (page - 1) * page_size
		end = start + page_size
		paginated_data = tfidf_data[start:end]

		serializer = DocumentStatisticsSerializer(
			{"tfidf_data": paginated_data},
			context={"document": doc}
		)
		return Response({
			"document_id": doc.id,
			"collection_id": collection_id,
			"page": page,
			"page_size": page_size,
			"total_words": len(tfidf_data),
			"tfidf_data": serializer.data['tfidf_data']
		})


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
		collections = Collection.objects.filter(user=request.user).order_by('-id')
		result_page = paginator.paginate_queryset(collections, request)
		serializer = CollectionSerializer(result_page, many=True)
		return paginator.get_paginated_response(serializer.data)


class CollectionDetailView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, collection_id):
		collection = get_object_or_404(Collection, id=collection_id, user=request.user)
		serializer = CollectionSerializer(collection)
		return Response(serializer.data)


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
		collection.save()

		try:
			update_collection_statistics_in_mongo(collection)
		except Exception as e:
			return Response({"error": f"Failed to update collection statistics: {e}"}, status=500)

		return Response({"status": "Document added and collection statistics updated successfully."})


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
