from django.contrib import admin
from .models import PID_db

class PID_dbAdmin(admin.ModelAdmin):
    list_display = ("id", "sim_time")

admin.site.register(PID_db, PID_dbAdmin)