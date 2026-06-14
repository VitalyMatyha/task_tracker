from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from employees.models import Employee
from employees.serializers import EmployeeSerializer, EmployeeBusySerializer
from tasks.models import Task


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с сотрудниками.

    Доступные операции:
        - GET /employees/ — список сотрудников
        - POST /employees/ — создание сотрудника
        - GET /employees/{id}/ — получение сотрудника
        - PUT/PATCH /employees/{id}/ — обновление сотрудника
        - DELETE /employees/{id}/ — удаление сотрудника
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class BusyEmployeesView(APIView):
    """
    Эндпоинт для получения списка занятых сотрудников.

    Возвращает список сотрудников вместе с их задачами,
    отсортированный по количеству активных задач (status != 'done')
    по убыванию.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос.

        Returns:
            Response: список сотрудников с количеством активных задач
            и списком задач, отсортированный по загруженности.
        """
        employees = Employee.objects.annotate(
            active_tasks_count=Count(
                'tasks',
                filter=~Q(tasks__status=Task.Status.DONE)
            )
        ).order_by('-active_tasks_count')

        serializer = EmployeeBusySerializer(employees, many=True)
        return Response(serializer.data)