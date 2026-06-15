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

    def validate(self, attrs):
        """
        Общая валидация объекта задачи.

        Проверяет, что задача не может быть родительской
        задачей для самой себя.
        """
        parent_task = attrs.get('parent_task')

        if parent_task and self.instance and parent_task.id == self.instance.id:
            raise serializers.ValidationError(
                {'parent_task': 'Задача не может быть родительской для самой себя.'}
            )

        return attrs


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