from django.contrib import admin
from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админ-панель для модели задачи."""
    list_display = ['id', 'title', 'assignee', 'status', 'deadline', 'parent_task']
    list_filter = ['status']
    search_fields = ['title']
