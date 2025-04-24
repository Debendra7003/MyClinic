from django.contrib import admin
from .models import LabTest, LabReport

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test_type', 'scheduled_date', 'status', 'created_at')
    search_fields = ('patient__user__username', 'test_type')
    list_filter = ('status',)

@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ('lab_test', 'published_at', 'description')
    search_fields = ('lab_test__test_type', 'description')