from django.contrib import admin
from .models import AppApp, Application, Appointment, CustomUser


admin.site.register(AppApp)
admin.site.register(Application)
admin.site.register(Appointment)
admin.site.register(CustomUser)