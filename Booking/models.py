from django.db import models
from django.contrib.auth.models import User

from TaskManager.models import Computer
# Create your models here.


class Status(models.Model):
    name = models.CharField(max_length=50)
    verbose_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.verbose_name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Комп'ютер")
    start_time = models.DateTimeField(verbose_name="Час початку бронювання")
    end_time = models.DateTimeField(verbose_name="Час завершення бронювання")
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, verbose_name="Додаткова інформація", null=True, blank=True, default=None)
    reason = models.CharField(max_length=255, verbose_name="Інформація від адміністратора/модератора", null=True, blank=True, default=None)

    def __str__(self):
        return f"Бронь: {self.computer.name} | {self.start_time}-{self.end_time}"


class BookingLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100, verbose_name="Дія", null=True, blank=True) # Змінено на CharField для спрощення
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата-час події")

    def __str__(self):
        return f"{self.timestamp}: {self.booking.computer.name}-{self.user.username}-{self.action}"
