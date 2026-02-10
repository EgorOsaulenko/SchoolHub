from django.db import models

# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Локація: {self.name}"

class Resource(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    type = models.CharField(max_length=255, verbose_name="Тип")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Розташування")
    is_active = models.BooleanField(default=True, verbose_name="Доступність")
    description = models.TextField(verbose_name="Опис", null=True, blank=True, default=None)


    def __str__(self):
        return f"{self.name}: {self.type}|{self.location.name}"


