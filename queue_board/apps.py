from django.apps import AppConfig
import threading

def create_default_superuser():
    from django.contrib.auth.models import User
    from django.db.utils import OperationalError
    try:
        # Create Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            
        # Create dedicated Staff user
        if not User.objects.filter(username='staff').exists():
            staff_user = User.objects.create_user('staff', 'staff@example.com', 'staff123')
            staff_user.is_staff = True
            staff_user.save()
            
    except OperationalError:
        pass
    except Exception:
        pass

class QueueBoardConfig(AppConfig):
    name = 'queue_board'

    def ready(self):
        threading.Thread(target=create_default_superuser).start()
