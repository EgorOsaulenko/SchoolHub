from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Action(models.Model):
    class ActionChoise(models.TextChoices):
        MANAGE_COMPUTERS = "MC", _("Керування комп'ютерами")
        MANAGE_TARIFFS = "MT", _("Керування тарифами")
        MANAGE_SESSIONS = "MS", _("Керування сесіями")
        VIEW_STATISTICS = "VS", _("Перегляд статистики")
        CREATE_BOOKING = "CB", _("Створення бронювань")
        MANAGE_BOOKINGS = "MB", _("Керування бронюваннями")

    name = models.CharField(
        max_length=100, 
        verbose_name="Дозволена дія", 
        help_text="Введіть назву дії",
        choices=ActionChoise.choices,
        default=ActionChoise.VIEW_STATISTICS
    )

    def __str__(self):
        return f"Назва дії: {self.name}"


class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name="Посада", help_text="Введіть назву посади")
    actions = models.ManyToManyField(Action, verbose_name="Список дозволів", help_text="Виберіть дії, які можна виконувати")

    def __str__(self):
        return f"Посада: {self.name}|Дії: {', '.join([action.name for action in self.actions.all()])}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    positions = models.ManyToManyField(Position, blank=True, default=None)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Баланс (грн)")
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", verbose_name="Аватарка", null=True, blank=True, default=None)
    bio = models.TextField(verbose_name="Про себе", null=True, blank=True, default=None)
    phone_number = models.CharField(max_length=20, null=True, blank=True, default=None, verbose_name="Номер телефону", help_text="Введіть номер телефону")

    def __str__(self):
        return f"Користувач: {self.user.get_full_name()} | Баланс: {self.balance} грн"