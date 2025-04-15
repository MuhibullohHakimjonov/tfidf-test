from django.db import models


class Document(models.Model):
	file = models.FileField(upload_to='documents/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Document {self.id} uploaded at {self.uploaded_at}"


class WordOccurrence(models.Model):
	word = models.CharField(max_length=255)
	document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='word_occurrences')
	count = models.PositiveIntegerField()

	class Meta:
		unique_together = ('word', 'document')

	def __str__(self):
		return f"{self.word} in Document {self.document.id} (Count: {self.count})"
