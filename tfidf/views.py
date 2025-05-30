from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .mongo import get_files_collection, get_mongo_collections
from .utils import compute_tfidf_for_documents
from datetime import datetime

MAX_FILE_SIZE = 9 * 1024 * 1024


class TFIDFMongoUploadView(APIView):
	parser_classes = [MultiPartParser]

	def post(self, request):
		files = request.FILES.getlist("file")
		if not files:
			return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

		if any(f.size > MAX_FILE_SIZE for f in files):
			return Response({"error": "Each file must be under 9MB"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			texts = []
			for f in files:
				text = f.read().decode('utf-8').strip()
				texts.append(text)
		except UnicodeDecodeError as e:
			return Response({"error": "Unable to decode one or more files"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			tfidf_results, word_counts = compute_tfidf_for_documents(texts)
			files_collection = get_files_collection()
			response_data = []

			for file, text, metrics, word_count in zip(files, texts, tfidf_results, word_counts):
				doc_data = {
					"file_name": file.name,
					"file_size": file.size,
					"word_count": word_count,
					"content": text,
					"tfidf_data": metrics,
					"uploaded_at": datetime.utcnow().isoformat()
				}
				file_id = files_collection.insert_one(doc_data).inserted_id

				response_data.append({
					"file_id": str(file_id),
					"file_name": file.name,
					"file_size": file.size,
					"word_count": word_count,
					"metrics": metrics
				})

			return Response({
				"message": "Files processed and stored successfully in MongoDB",
				"results": response_data
			}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({"error": "Failed to save metrics"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MetricsView(APIView):
	def get(self, request):
		try:
			collections = get_mongo_collections()
			files = list(collections["files_collection"].find({}))

			if not files:
				return Response({"message": "No data available"}, status=status.HTTP_204_NO_CONTENT)

			word_counts = [f.get("word_count", 0) for f in files]
			file_sizes = [f.get("file_size", 0) for f in files]
			timestamps = [
				datetime.fromisoformat(f["uploaded_at"]) for f in files if "uploaded_at" in f
			]

			metrics = {
				"files_processed": len(files),
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
		return Response({'version': '1.3'}, status.HTTP_200_OK)
