import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from queue_board.models import Token

count, _ = Token.objects.all().delete()
print(f"Deleted {count} tokens successfully. The queue is now completely clear.")
