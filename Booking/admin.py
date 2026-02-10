from django.contrib import admin

from .models import Status, Booking, BookingLog, Action

# Register your models here.


admin.site.register([Status, Booking, BookingLog, Action])