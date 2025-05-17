from django.contrib import admin
from .models import Nurse

@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'department', 'nurse_id', 'created_at', 'updated_at')
    search_fields = ('user_id', 'department', 'nurse_id')
    list_filter = ('department', 'created_at')
