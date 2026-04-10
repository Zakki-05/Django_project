from django.db import models
from django.utils import timezone
from datetime import timedelta

class ClinicSetting(models.Model):
    name = models.CharField(max_length=100, default="M.B Shifa Clinic")
    address = models.CharField(max_length=255, default="WPP8+HF Peranampattu, Tamil Nadu 635810")
    latitude = models.FloatField(default=12.9364375)
    longitude = models.FloatField(default=78.7161875)
    average_consultation_time_minutes = models.IntegerField(default=15)
    max_tokens_per_day = models.IntegerField(default=50)

    def __str__(self):
        return self.name

class Patient(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"

class Token(models.Model):
    TOKEN_STATUS_CHOICES = (
        ('INACTIVE', 'Inactive (Outside Range)'),
        ('ACTIVE', 'Active (Waiting)'),
        ('SERVING', 'Currently Serving'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('SKIPPED', 'Skipped'),
    )

    DEPARTMENT_CHOICES = (
        ('GENERAL', 'General Physician'),
        ('PEDIATRICS', 'Pediatrics'),
        ('DENTAL', 'Dental'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tokens')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='GENERAL')
    token_number = models.IntegerField()
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=15, choices=TOKEN_STATUS_CHOICES, default='INACTIVE')
    generated_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    is_priority = models.BooleanField(default=False)

    class Meta:
        unique_together = ('token_number', 'date')
        ordering = ['-is_priority', 'token_number']

    def __str__(self):
        return f"Token #{self.token_number} - {self.patient.name}"

    def get_estimated_wait_minutes(self):
        if self.status != 'ACTIVE':
            return 0
        clinic_config = ClinicSetting.objects.first()
        avg_time = clinic_config.average_consultation_time_minutes if clinic_config else 15
        
        # Number of tokens ahead based on is_priority and token_number
        if self.is_priority:
            ahead_count = Token.objects.filter(
                date=self.date,
                status='ACTIVE',
                is_priority=True,
                token_number__lt=self.token_number
            ).count()
        else:
            priority_count = Token.objects.filter(
                date=self.date,
                status='ACTIVE',
                is_priority=True
            ).count()
            regular_ahead = Token.objects.filter(
                date=self.date,
                status='ACTIVE',
                is_priority=False,
                token_number__lt=self.token_number
            ).count()
            ahead_count = priority_count + regular_ahead

        return ahead_count * avg_time
