from django.contrib import admin
from .models import Administrator


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'employee_id', 'department', 'access_level')
    search_fields = ('user_id', 'employee_id', 'department')
    list_filter = ('department', 'access_level') 