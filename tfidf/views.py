from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .mongo import get_documents_collection, get_mongo_collections
from .utils import compute_global_tfidf_table
from datetime import datetime

MAX_FILE_SIZE = 8 * 1024 * 1024


class TFIDFMongoUploadView(APIView):
	parser_classes = [MultiPartParser]

	def post(self, request):
		files = request.FILES.getlist("file")
		if not files:
			return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

		oversized = [f.name for f in files if f.size > MAX_FILE_SIZE]
		if oversized:
			return Response(
				{"error": f"Files too large: {', '.join(oversized)}"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			texts = [f.read().decode('utf-8').strip() for f in files]
		except UnicodeDecodeError:
			return Response({"error": "Unable to decode one or more files"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			tfidf_results, word_counts = compute_global_tfidf_table(texts)
			documents_collection = get_documents_collection()

			now = datetime.utcnow().isoformat()

			# Подготовка всех документов
			documents = []
			for f, text, tfidf, wc in zip(files, texts, tfidf_results, word_counts):
				documents.append({
					"file_name": f.name,
					"file_size": f.size,
					"word_count": wc,
					"content": text,
					"tfidf_data": tfidf,
					"uploaded_at": now
				})

			# Массовая вставка
			result = documents_collection.insert_many(documents)
			inserted_ids = result.inserted_ids

			# Считаем топ-50 по IDF из первого документа
			top_words = []
			if tfidf_results:
				for i, item in enumerate(tfidf_results[0][:50]):
					word = item["word"]
					idf = item["idf"]
					avg_tf = sum(doc[i]["tf"] for doc in tfidf_results if i < len(doc)) / len(tfidf_results)
					top_words.append({
						"word": word,
						"idf": round(idf, 6),
						"avg_tf": round(avg_tf, 6)
					})

			return Response({
				"message": "Files processed and stored successfully in MongoDB",
				"files": [
					{
						"file_id": str(fid),
						"file_name": f.name,
						"file_size": f.size,
						"word_count": wc
					}
					for f, wc, fid in zip(files, word_counts, inserted_ids)
				],
				"top_words": top_words
			}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({"error": f"Failed to process files: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
		return Response({'version': '1.3'}, status=status.HTTP_200_OK)
