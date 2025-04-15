from django.contrib import admin
from .models import Document


class DocumentAdmin(admin.ModelAdmin):
	date_hierarchy = "uploaded_at"
	list_display = ['id', 'file', 'uploaded_at']
	list_display_links = ['id']


admin.site.register(Document, DocumentAdmin)
