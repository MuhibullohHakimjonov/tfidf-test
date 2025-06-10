from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
	list_display = ['id', 'email', 'username', 'is_active', 'is_staff', 'date_joined']
	list_display_links = ['id', 'email']
