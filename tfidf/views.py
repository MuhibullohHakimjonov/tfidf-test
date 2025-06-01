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

		if any(f.size > MAX_FILE_SIZE for f in files):
			return Response({"error": "Each file must be under 8MB"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			texts = []
			for f in files:
				text = f.read().decode('utf-8').strip()
				texts.append(text)
		except UnicodeDecodeError:
			return Response({"error": "Unable to decode one or more files"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			# Вычисляем глобальную таблицу TF-IDF
			tfidf_results, word_counts = compute_global_tfidf_table(texts)
			documents_collection = get_documents_collection()
			file_ids = []

			# Сохраняем данные каждого документа в MongoDB
			for file, text, metrics, word_count in zip(files, texts, tfidf_results, word_counts):
				doc_data = {
					"file_name": file.name,
					"file_size": file.size,
					"word_count": word_count,
					"content": text,
					"tfidf_data": metrics,
					"uploaded_at": datetime.utcnow().isoformat()
				}
				file_id = documents_collection.insert_one(doc_data).inserted_id
				file_ids.append(file_id)

			# Вычисляем топ-50 слов с их IDF и средним TF
			if tfidf_results:
				num_words = len(tfidf_results[0])  # Учитываем случай, если слов меньше 50
				top_words = []
				for i in range(num_words):
					word_data = tfidf_results[0][i]
					word = word_data["word"]
					idf = word_data["idf"]
					tfs = [doc[i]["tf"] for doc in tfidf_results]  # Собираем TF из всех документов
					avg_tf = sum(tfs) / len(tfs)  # Среднее TF
					top_words.append({
						"word": word,
						"idf": round(idf, 6),
						"avg_tf": round(avg_tf, 6)
					})
			else:
				top_words = []

			# Формируем ответ
			return Response({
				"message": "Files processed and stored successfully in MongoDB",
				"files": [
					{
						"file_id": str(file_id),
						"file_name": file.name,
						"file_size": file.size,
						"word_count": word_count
					} for file, word_count, file_id in zip(files, word_counts, file_ids)
				],
				"top_words": top_words
			}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({"error": f"Failed to save metrics: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
