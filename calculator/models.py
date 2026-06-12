from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Calculation(models.Model):
    OPERATION_CHOICES = [
        ('add', '➕ Сложение'),
        ('subtract', '➖ Вычитание'),
        ('multiply', '✖️ Умножение'),
        ('divide', '➗ Деление'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calculations')
    num1 = models.FloatField(validators=[MinValueValidator(-1e15), MaxValueValidator(1e15)])
    num2 = models.FloatField(validators=[MinValueValidator(-1e15), MaxValueValidator(1e15)])
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    result = models.FloatField(null=True, blank=True)
    error_message = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        op = dict(self.OPERATION_CHOICES).get(self.operation, self.operation)
        return f'{self.num1} {op} {self.num2} = {self.result if self.error_message == "" else self.error_message}'
    