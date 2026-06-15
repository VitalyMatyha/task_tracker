from django.contrib import admin
from employees.models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Админ-панель для модели сотрудника."""
    list_display = ['id', 'full_name', 'position']
    search_fields = ['full_name', 'position']
