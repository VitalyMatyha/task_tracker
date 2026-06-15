from rest_framework import serializers
from employees.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели сотрудника.

    Используется для CRUD операций с сотрудниками.
    """

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position']


class EmployeeBusySerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения загруженности сотрудника.

    Дополнительно возвращает количество активных задач
    и список задач сотрудника.
    """

    active_tasks_count = serializers.IntegerField(
        read_only=True,
        help_text='Количество активных задач сотрудника'
    )
    tasks = serializers.StringRelatedField(
        many=True,
        read_only=True,
        help_text='Список задач сотрудника'
    )

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'active_tasks_count', 'tasks']
