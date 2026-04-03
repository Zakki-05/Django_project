import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from django.contrib.auth.models import User

user, created = User.objects.get_or_create(username='staff')
user.set_password('password123')
user.is_staff = True
user.save()
print("Created staff user: staff / password123")
