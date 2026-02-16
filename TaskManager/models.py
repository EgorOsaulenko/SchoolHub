from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Zone(models.Model):
    name = models.CharField(max_length=50, verbose_name="Назва зони")
    description = models.TextField(verbose_name="Опис", blank=True)

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва тарифу")
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Ціна за годину (грн)")
    
    def __str__(self):
        return f"{self.name} ({self.price_per_hour} грн/год)"


class Computer(models.Model):
    class StatusChoice(models.TextChoices):
        FREE = "FR", "Вільний"
        BUSY = "BS", "Зайнятий" 
        MAINTENANCE = "MT", "Технічні роботи"
        BOOKED = "BK", "Заброньовано"

    name = models.CharField(max_length=50, verbose_name="Номер/Назва ПК")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="Ігрова зона")
    ip_address = models.GenericIPAddressField(verbose_name="IP адреса", null=True, blank=True)
    status = models.CharField(max_length=2, choices=StatusChoice.choices, default=StatusChoice.FREE, verbose_name="Статус")

    def __str__(self):
        return f"{self.name} [{self.get_status_display()}]"


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клієнт")
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, verbose_name="Комп'ютер")
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, verbose_name="Тариф")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Початок сесії")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Кінець сесії")
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name="Вартість")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return f"Сесія {self.user.username} на {self.computer.name}"


class Payment(models.Model):
    class PaymentType(models.TextChoices):
        DEPOSIT = "DP", "Поповнення рахунку"
        SESSION_PAYMENT = "SP", "Оплата сесії"
        REFUND = "RF", "Повернення коштів"

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума")
    payment_type = models.CharField(max_length=2, choices=PaymentType.choices, verbose_name="Тип платежу")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата транзакції")

    def __str__(self):
        return f"{self.get_payment_type_display()}: {self.amount} грн ({self.user.username})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('approved', 'Підтверджено'),
        ('rejected', 'Відхилено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач", related_name='taskmanager_bookings')
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, verbose_name="Комп'ютер", related_name='taskmanager_bookings')
    start_time = models.DateTimeField(verbose_name="Час початку")
    duration = models.IntegerField(help_text="Тривалість у годинах", verbose_name="Тривалість")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f"Бронювання {self.user} на {self.computer}"