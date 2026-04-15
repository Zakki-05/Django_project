import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from queue_board.models import Staff
from django.utils import timezone

def seed():
    print("Seeding staff records...")
    s, created = Staff.objects.get_or_create(
        name="Dr. Sameer Khan",
        defaults={
            'role': "Chief Medical Officer",
            'qualification': "MD, MBBS (Internal Medicine)",
            'experience': "12 Years",
            'phone': "+91 98765 43210",
            'email': "sameer.khan@shifaclinic.com",
            'image': "staff_images/doctor_demo.png",
            'joined_date': timezone.now().date()
        }
    )
    if created:
        print(f"Added {s.name}")
    else:
        print(f"{s.name} already exists")

if __name__ == "__main__":
    seed()
