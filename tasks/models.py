from django.db import models
from employees.models import Employee


class Task(models.Model):
    """
    Модель задачи.

    Attributes:
        title (str): Наименование задачи.
        parent_task (Task): Родительская задача (если есть зависимость).
        assignee (Employee): Исполнитель задачи.
        deadline (date): Срок выполнения задачи.
        status (str): Статус задачи (new, in_progress, done).
    """

    class Status(models.TextChoices):
        """Статусы задачи."""

        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В работе'
        DONE = 'done', 'Завершена'

    title = models.CharField(max_length=255, verbose_name='Наименование')
    parent_task = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subtasks',
        verbose_name='Родительская задача'
    )
    assignee = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tasks',
        verbose_name='Исполнитель'
    )
    deadline = models.DateField(verbose_name='Срок')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        """Возвращает строковое представление задачи."""
        return self.title
