from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Employee
from tasks.models import Task


class EmployeeModelTest(APITestCase):
    """Тесты модели Employee."""

    def test_str_representation(self):
        """Строковое представление сотрудника должно совпадать с ФИО."""
        employee = Employee.objects.create(full_name='Иванов Иван', position='Разработчик')
        self.assertEqual(str(employee), 'Иванов Иван')


class EmployeeCRUDTest(APITestCase):
    """Тесты CRUD операций для сотрудников."""

    def setUp(self):
        """Создаёт тестового сотрудника перед каждым тестом."""
        self.employee = Employee.objects.create(full_name='Иванов Иван', position='Разработчик')

    def test_list_employees(self):
        """Получение списка сотрудников возвращает статус 200."""
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_employee(self):
        """Создание сотрудника возвращает статус 201 и сохраняет запись в БД."""
        url = reverse('employee-list')
        data = {'full_name': 'Петров Петр', 'position': 'Тестировщик'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

    def test_retrieve_employee(self):
        """Получение конкретного сотрудника по id."""
        url = reverse('employee-detail', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Иванов Иван')

    def test_update_employee(self):
        """Обновление данных сотрудника через PATCH."""
        url = reverse('employee-detail', args=[self.employee.id])
        response = self.client.patch(url, {'position': 'Senior Разработчик'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.position, 'Senior Разработчик')

    def test_delete_employee(self):
        """Удаление сотрудника возвращает статус 204 и удаляет запись из БД."""
        url = reverse('employee-detail', args=[self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 0)


class BusyEmployeesTest(APITestCase):
    """Тесты эндпоинта получения занятых сотрудников."""

    def setUp(self):
        """Создаёт сотрудников и задачи с разной нагрузкой."""
        self.employee_busy = Employee.objects.create(full_name='Иванов Иван', position='Разработчик')
        self.employee_free = Employee.objects.create(full_name='Петров Петр', position='Тестировщик')

        deadline = date.today() + timedelta(days=5)

        Task.objects.create(
            title='Задача 1', assignee=self.employee_busy,
            deadline=deadline, status=Task.Status.NEW
        )
        Task.objects.create(
            title='Задача 2', assignee=self.employee_busy,
            deadline=deadline, status=Task.Status.IN_PROGRESS
        )
        Task.objects.create(
            title='Задача 3', assignee=self.employee_free,
            deadline=deadline, status=Task.Status.DONE
        )

    def test_busy_employees_order(self):
        """Сотрудники должны быть отсортированы по убыванию активных задач."""
        url = reverse('busy-employees')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[0]['full_name'], 'Иванов Иван')
        self.assertEqual(response.data[0]['active_tasks_count'], 2)

        self.assertEqual(response.data[1]['full_name'], 'Петров Петр')
        self.assertEqual(response.data[1]['active_tasks_count'], 0)