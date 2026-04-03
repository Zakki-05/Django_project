from django.contrib import admin
from .models import ClinicSetting, Patient, Token

admin.site.register(ClinicSetting)
admin.site.register(Patient)
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'patient', 'date', 'status', 'is_priority')
    list_filter = ('date', 'status', 'is_priority')
