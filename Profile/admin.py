from django.contrib import admin

from .models import Action, Position, Profile

# Register your models here.


admin.site.register([Action, Position, Profile])
