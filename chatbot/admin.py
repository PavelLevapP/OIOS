from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'user_name', 'first_name', 'last_name')
    search_fields = ('telegram_id', 'user_name', 'first_name', 'last_name')
