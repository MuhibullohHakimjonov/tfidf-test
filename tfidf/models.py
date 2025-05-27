from django.db import models


class FileUpload(models.Model):
	file_name = models.CharField(max_length=255)
	file_size = models.BigIntegerField()  # Размер в байтах
	word_count = models.IntegerField()
	uploaded_at = models.DateTimeField(auto_now_add=True)
	content = models.TextField()  # Для хранения текста файла

	def __str__(self):
		return f"{self.file_name} ({self.uploaded_at})"


class TFIDFMetric(models.Model):
	file = models.ForeignKey(FileUpload, related_name='metrics', on_delete=models.CASCADE)
	word = models.CharField(max_length=100)
	tf = models.FloatField()
	idf = models.FloatField()

	def __str__(self):
		return f"{self.word} (TF: {self.tf}, IDF: {self.idf})"
