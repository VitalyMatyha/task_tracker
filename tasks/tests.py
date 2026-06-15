from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Employee
from tasks.models import Task


class TaskModelTest(APITestCase):
    """Тесты модели Task."""

    def test_str_representation(self):
        """Строковое представление задачи должно совпадать с её наименованием."""
        task = Task.objects.create(title='Тестовая задача', deadline=date.today())
        self.assertEqual(str(task), 'Тестовая задача')


class TaskCRUDTest(APITestCase):
    """Тесты CRUD операций для задач."""

    def setUp(self):
        """Создаёт тестового сотрудника и задачу перед каждым тестом."""
        self.employee = Employee.objects.create(full_name='Иванов Иван', position='Разработчик')
        self.deadline = date.today() + timedelta(days=5)
        self.task = Task.objects.create(
            title='Тестовая задача',
            assignee=self.employee,
            deadline=self.deadline,
            status=Task.Status.NEW
        )

    def test_list_tasks(self):
        """Получение списка задач возвращает статус 200."""
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        """Создание задачи возвращает статус 201 и сохраняет запись в БД."""
        url = reverse('task-list')
        data = {
            'title': 'Новая задача',
            'deadline': self.deadline.isoformat(),
            'status': Task.Status.NEW,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_retrieve_task(self):
        """Получение конкретной задачи по id."""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Тестовая задача')

    def test_update_task(self):
        """Обновление статуса задачи через PATCH."""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.patch(url, {'status': Task.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)

    def test_delete_task(self):
        """Удаление задачи возвращает статус 204 и удаляет запись из БД."""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)


class TaskValidationTest(APITestCase):
    """Тесты валидации данных задачи."""

    def setUp(self):
        """Создаёт тестовую задачу перед каждым тестом."""
        self.task = Task.objects.create(
            title='Задача',
            deadline=date.today() + timedelta(days=5),
            status=Task.Status.NEW
        )

    def test_deadline_in_past_is_invalid(self):
        """Создание задачи с дедлайном в прошлом должно вернуть ошибку 400."""
        url = reverse('task-list')
        data = {
            'title': 'Задача с прошлым сроком',
            'deadline': (date.today() - timedelta(days=1)).isoformat(),
            'status': Task.Status.NEW,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('deadline', response.data)

    def test_self_parent_task_is_invalid(self):
        """Задача не может быть родительской для самой себя."""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.patch(url, {'parent_task': self.task.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent_task', response.data)


class ImportantTasksTest(APITestCase):
    """Тесты эндпоинта получения важных задач."""

    def setUp(self):
        """
        Создаёт сотрудников и задачи для проверки логики важных задач.

        Структура:
            - Сотрудник 1: задача-родитель (статус 'new')
            - Сотрудник 2: задача-потомок (статус 'in_progress',
              parent_task = задача сотрудника 1)
        """
        self.employee1 = Employee.objects.create(full_name='Иванов Иван', position='Разработчик')
        self.employee2 = Employee.objects.create(full_name='Петров Петр', position='Тестировщик')

        self.deadline = date.today() + timedelta(days=5)

        self.parent_task = Task.objects.create(
            title='Родительская задача',
            assignee=self.employee1,
            deadline=self.deadline,
            status=Task.Status.NEW
        )

        self.child_task = Task.objects.create(
            title='Дочерняя задача',
            assignee=self.employee2,
            parent_task=self.parent_task,
            deadline=self.deadline,
            status=Task.Status.IN_PROGRESS
        )

    def test_important_tasks_returns_parent_task(self):
        """Родительская задача 'new' с дочерней 'in_progress' попадает в важные."""
        url = reverse('important-tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], 'Родительская задача')

    def test_important_tasks_includes_candidates(self):
        """Список кандидатов должен включать исполнителя зависимой задачи."""
        url = reverse('important-tasks')
        response = self.client.get(url)
        employees = response.data[0]['employees']
        self.assertIn('Иванов Иван', employees)
        self.assertIn('Петров Петр', employees)

    def test_no_important_tasks_when_no_dependencies(self):
        """Если зависимых задач 'in_progress' нет, список важных задач пуст."""
        self.child_task.status = Task.Status.DONE
        self.child_task.save()

        url = reverse('important-tasks')
        response = self.client.get(url)
        self.assertEqual(response.data, [])
