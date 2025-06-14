from django.contrib import admin
from .models import Document, Collection


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
	list_display = ['id', 'user', 'name', 'word_count']
	list_display_links = ['id', 'user']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
	list_display = ['id', 'user', 'name', 'created_at']
	list_display_links = ['id', 'user']
