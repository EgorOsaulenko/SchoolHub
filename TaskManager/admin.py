from django.contrib import admin

from .models import Zone, Tariff, Computer, Session, Payment

# Register your models here.


admin.site.register([Zone, Tariff, Computer, Session, Payment])