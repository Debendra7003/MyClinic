from django.contrib import admin
from .models import Clinic, Insurance

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'created_at')
    search_fields = ('name', 'address')

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('provider', 'policy_number', 'user', 'created_at')
    search_fields = ('provider', 'policy_number')