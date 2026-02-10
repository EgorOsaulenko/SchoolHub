from django.contrib import admin

from .models import Location, Resource

# Register your models here.


admin.site.register([Location, Resource])
