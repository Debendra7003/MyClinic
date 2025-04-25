from django.contrib import admin
# from .models import PatientProfile, Prescription, AmbulanceRequest
from .models import PatientProfile, Prescription

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'phone')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'uploaded_at', 'description')
    search_fields = ('patient__user__username', 'description')

# @admin.register(AmbulanceRequest)
# class AmbulanceRequestAdmin(admin.ModelAdmin):
#     list_display = ('patient', 'location', 'status', 'created_at')
#     search_fields = ('patient__user__username', 'location')