# Трекер задач сотрудников

REST API приложение для управления задачами и сотрудниками компании. Позволяет распределять задачи между сотрудниками, отслеживать загруженность и выявлять важные задачи, требующие приоритетного внимания.

## Стек технологий

- Python 3.12+
- Django 6
- Django REST Framework
- PostgreSQL
- drf-spectacular (Swagger/ReDoc документация)
- Docker, Docker Compose
- Coverage (тестирование)

## Структура проекта

task_tracker/

├── core/                   # настройки проекта, главный urls.py

├── employees/              # приложение "Сотрудники"

│   ├── models.py           # модель Employee

│   ├── serializers.py      # сериализаторы

│   ├── views.py             # ViewSet + BusyEmployeesView

│   ├── urls.py

│   ├── admin.py

│   └── tests.py

├── tasks/                  # приложение "Задачи"

│   ├── models.py           # модель Task

│   ├── serializers.py

│   ├── views.py             # ViewSet + ImportantTasksView

│   ├── urls.py

│   ├── admin.py

│   └── tests.py

├── manage.py

├── requirements.txt

├── Dockerfile

├── docker-compose.yml

└── .env                    # переменные окружения (не в репозитории)

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <ссылка на репозиторий>
cd task_tracker
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
DB_NAME=task_tracker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

После запуска приложение доступно по адресу: `http://127.0.0.1:8000/`

### 4. Создание суперпользователя (для админки)

```bash
docker-compose exec web python manage.py createsuperuser
```

## Документация API

После запуска проекта документация доступна по адресам:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI схема: `http://127.0.0.1:8000/api/schema/`

## Эндпоинты API

### Сотрудники

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/employees/` | Список сотрудников |
| POST | `/api/employees/` | Создание сотрудника |
| GET | `/api/employees/{id}/` | Получение сотрудника |
| PUT/PATCH | `/api/employees/{id}/` | Обновление сотрудника |
| DELETE | `/api/employees/{id}/` | Удаление сотрудника |
| GET | `/api/employees/busy/` | Список занятых сотрудников с их задачами, отсортированный по нагрузке |

### Задачи

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/tasks/` | Список задач |
| POST | `/api/tasks/` | Создание задачи |
| GET | `/api/tasks/{id}/` | Получение задачи |
| PUT/PATCH | `/api/tasks/{id}/` | Обновление задачи |
| DELETE | `/api/tasks/{id}/` | Удаление задачи |
| GET | `/api/tasks/important/` | Список важных задач с подходящими исполнителями |

## Логика эндпоинта "Важные задачи"

Важная задача — задача со статусом `new`, от которой зависит хотя бы одна другая задача со статусом `in_progress` (то есть является родительской для задачи, взятой в работу).

Для каждой важной задачи определяется список сотрудников, которые могут взять её в работу:

- наименее загруженный сотрудник (или несколько, если у них одинаковое минимальное количество активных задач);
- сотрудник, выполняющий зависимую (дочернюю) задачу в статусе `in_progress`, если его нагрузка не более чем на 2 задачи превышает нагрузку наименее загруженного сотрудника.

## Тестирование

Запуск тестов с измерением покрытия:

```bash
coverage run manage.py test
coverage report
```

Текущее покрытие тестами: **99%**.

## Модели данных

### Employee (Сотрудник)

| Поле | Тип | Описание |
|---|---|---|
| full_name | CharField | ФИО сотрудника |
| position | CharField | Должность |

### Task (Задача)

| Поле | Тип | Описание |
|---|---|---|
| title | CharField | Наименование задачи |
| parent_task | ForeignKey (self) | Родительская задача |
| assignee | ForeignKey (Employee) | Исполнитель |
| deadline | DateField | Срок выполнения |
| status | CharField (choices) | Статус: new / in_progress / done |