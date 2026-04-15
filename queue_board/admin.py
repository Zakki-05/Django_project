from django.contrib import admin
from .models import ClinicSetting, Patient, Token, Staff

admin.site.site_header = "M.B Shifa Clinic Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the Data Management Portal"

@admin.register(ClinicSetting)
class ClinicSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'average_consultation_time_minutes', 'max_tokens_per_day')
    search_fields = ('name', 'address')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'created_at')
    search_fields = ('name', 'phone_number')
    list_filter = ('created_at',)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'patient', 'department', 'date', 'status', 'is_priority')
    list_filter = ('date', 'status', 'department', 'is_priority')
    search_fields = ('patient__name', 'patient__phone_number', 'token_number')
    readonly_fields = ('generated_at',)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'qualification', 'phone', 'joined_date')
    search_fields = ('name', 'role', 'qualification', 'email')
    list_filter = ('role', 'joined_date')
