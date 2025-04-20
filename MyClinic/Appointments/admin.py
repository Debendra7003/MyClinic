from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'clinic', 'doctor', 'start_time', 'status', 'created_at')
    search_fields = ('patient__user__username', 'clinic__name', 'doctor__username')
    list_filter = ('status',)