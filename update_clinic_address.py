import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from queue_board.models import ClinicSetting

clinic = ClinicSetting.objects.first()
if clinic:
    clinic.address = "WPP8+HF Peranampattu, Tamil Nadu 635810"
    clinic.latitude = 12.9364375
    clinic.longitude = 78.7161875
    clinic.save()
    print(f"Updated Clinic Setting: {clinic.address}")
    print(f"Coordinates: {clinic.latitude}, {clinic.longitude}")
else:
    ClinicSetting.objects.create(
        address="WPP8+HF Peranampattu, Tamil Nadu 635810",
        latitude=12.9364375,
        longitude=78.7161875
    )
    print("Created new Clinic Setting with provided address and coordinates.")
