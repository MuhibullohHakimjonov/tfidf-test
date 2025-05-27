from .models import FileUpload, TFIDFMetric
from .utils import compute_tfidf_for_documents
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

MAX_FILE_SIZE = 10 * 1024 * 1024


class TFIDFNoDBView(APIView):
	parser_classes = [MultiPartParser]

	def post(self, request):
		files = request.FILES.getlist("file")
		if not files:
			return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

		if any(f.size > MAX_FILE_SIZE for f in files):
			return Response({"error": "Each file must be under 10MB"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			texts = [f.read().decode("utf-8") for f in files]
		except UnicodeDecodeError:
			return Response({"error": "Unable to decode one or more files"}, status=status.HTTP_400_BAD_REQUEST)
		tfidf_results = compute_tfidf_for_documents(texts)

		response_data = []

		for file, text, result in zip(files, texts, tfidf_results):
			file_upload = FileUpload.objects.create(
				file_name=file.name,
				file_size=file.size,
				word_count=len(text.split()),
				content=text
			)

			for metric in result:
				TFIDFMetric.objects.create(
					file=file_upload,
					word=metric['word'],
					tf=metric['tf'],
					idf=metric['idf'],
				)

			response_data.append({
				"file_name": file.name,
				"file_size": file.size,
				"metrics": result
			})

		return Response({
			"message": "Files processed and data saved successfully",
			"results": response_data
		}, status=status.HTTP_200_OK)
