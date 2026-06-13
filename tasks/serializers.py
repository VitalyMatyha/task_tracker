from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели задачи.

    Используется для CRUD операций с задачами.
    """

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'parent_task',
            'assignee',
            'deadline',
            'status',
        ]

    def validate_deadline(self, value):
        """
        Валидация срока выполнения задачи.

        Проверяет что дедлайн не в прошлом.
        """
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError(
                'Срок выполнения задачи не может быть в прошлом.'
            )
        return value


class ImportantTaskSerializer(serializers.Serializer):
    """
    Сериализатор для важных задач.

    Возвращает важную задачу, срок и список подходящих сотрудников.
    """

    task = serializers.CharField(
        help_text='Наименование важной задачи'
    )
    deadline = serializers.DateField(
        help_text='Срок выполнения задачи'
    )
    employees = serializers.ListField(
        child=serializers.CharField(),
        help_text='Список сотрудников которые могут взять задачу'
    )