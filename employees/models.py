from django.db import models


class Employee(models.Model):
    """
    Модель сотрудника.
    """

    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    position = models.CharField(max_length=255, verbose_name='Должность')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        """Возвращает строковое представление сотрудника."""
        return self.full_name
