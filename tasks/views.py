from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from tasks.models import Task
from tasks.serializers import TaskSerializer, ImportantTaskSerializer
from employees.models import Employee


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с задачами.

    Доступные операции:
        - GET /tasks/ — список задач
        - POST /tasks/ — создание задачи
        - GET /tasks/{id}/ — получение задачи
        - PUT/PATCH /tasks/{id}/ — обновление задачи
        - DELETE /tasks/{id}/ — удаление задачи
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class ImportantTasksView(APIView):
    """
    Эндпоинт для получения важных задач.

    Важная задача — это задача со статусом 'new', от которой
    зависит хотя бы одна другая задача со статусом 'in_progress'
    (то есть является родительской для задачи, взятой в работу).

    Для каждой важной задачи определяется список сотрудников,
    которые могут взять её в работу:
        - наименее загруженный сотрудник (или несколько, если у них
          одинаковое минимальное количество активных задач);
        - сотрудник, выполняющий зависимую (дочернюю) задачу в статусе
          'in_progress', если его нагрузка не более чем на 2 задачи
          превышает нагрузку наименее загруженного сотрудника.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос.

        Returns:
            Response: список объектов вида
            {task, deadline, employees: [ФИО, ...]}.
        """
        employees = Employee.objects.annotate(
            active_tasks_count=Count(
                'tasks',
                filter=~Q(tasks__status=Task.Status.DONE)
            )
        )

        if employees.exists():
            min_load = min(emp.active_tasks_count for emp in employees)
        else:
            min_load = 0

        important_tasks = Task.objects.filter(
            status=Task.Status.NEW,
            subtasks__status=Task.Status.IN_PROGRESS
        ).distinct()

        result = []
        for task in important_tasks:
            candidates = set()

            # Наименее загруженные сотрудники
            for emp in employees:
                if emp.active_tasks_count == min_load:
                    candidates.add(emp.full_name)

            # Сотрудники, выполняющие зависимые (дочерние) задачи в работе
            dependent_assignees = employees.filter(
                tasks__parent_task=task,
                tasks__status=Task.Status.IN_PROGRESS
            ).distinct()

            for emp in dependent_assignees:
                if emp.active_tasks_count <= min_load + 2:
                    candidates.add(emp.full_name)

            result.append({
                'task': task.title,
                'deadline': task.deadline,
                'employees': list(candidates)
            })

        serializer = ImportantTaskSerializer(result, many=True)
        return Response(serializer.data)