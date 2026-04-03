import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from django.contrib.auth.models import User
from queue_board.models import ClinicSetting

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
if not ClinicSetting.objects.exists():
    ClinicSetting.objects.create()
    print("Clinic setting created.")
print("Init ready.")
