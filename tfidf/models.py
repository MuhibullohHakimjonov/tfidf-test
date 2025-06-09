from django.db import models
from django.conf import settings



class Document(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	path = models.TextField()
	size = models.IntegerField()
	word_count = models.IntegerField()
	mongo_id = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name


class Collection(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="collections")
	name = models.CharField(max_length=255)
	documents = models.ManyToManyField(Document, related_name="collections")
	created_at = models.DateTimeField(auto_now_add=True)
