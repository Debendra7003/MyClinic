from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class AdminAdmin(BaseUserAdmin):
    list_display = ["id", "first_name","last_name", "email", "mobile_number", "is_admin", "is_active"]
    list_filter = ["is_admin", "is_active"]

    fieldsets = [
        ('Admin Credentials', {"fields": ["mobile_number", "password"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]

    add_fieldsets = [
        (
            "Create Admin",
            {
                "classes": ["wide"],
                "fields": [ "mobile_number", "password1", "password2"],
            },
        ),
    ]

    search_fields = ["email","mobile_number"]
    ordering = ["id"]
    filter_horizontal = []


# Register the models in Django Admin
# admin.site.register(Customer, CustomerAdmin)
admin.site.register(User, AdminAdmin)
