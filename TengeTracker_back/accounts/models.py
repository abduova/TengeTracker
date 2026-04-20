from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):
    """A place where money is stored: cash, bank card, savings, etc."""
    name = models.CharField(max_length=100)
    balance = models.FloatField(default=0)
    icon = models.CharField(max_length=50, default='cash')
    color = models.CharField(max_length=20, default='#3b82f6')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=50, default='grossories')
    color = models.CharField(max_length=20, default='#ef4444')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='categories'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='expense'
    )

    def __str__(self):
        return f"{self.amount} - {self.category.name}"
