from django.db import models

# class FileUpload(models.Model):
# 	file = models.FileField(upload_to='uploads/')
# 	uploaded_at = models.DateTimeField(auto_now_add=True)
# 	word_count = models.PositiveIntegerField()
# 	tfidf_data = models.JSONField(null=True, blank=True)


# class TFIDFMetric(models.Model):
# 	file = models.ForeignKey(
# 		FileUpload,
# 		related_name='metrics',
# 		on_delete=models.CASCADE,
# 		verbose_name="File"
# 	)
# 	word = models.CharField(max_length=100, verbose_name="Word")
# 	tf = models.FloatField(verbose_name="Term Frequency")
# 	idf = models.FloatField(verbose_name="Inverse Document Frequency")
#
#
# class IDFMetric(models.Model):
# 	word = models.CharField(max_length=100, unique=True)
# 	document_count = models.PositiveIntegerField()
# 	idf = models.FloatField()
#
# 	def __str__(self):
# 		return f"{self.word}: IDF={self.idf:.3f}"
