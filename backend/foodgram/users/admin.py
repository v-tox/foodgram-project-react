from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'password',)
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
