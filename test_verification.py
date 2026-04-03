import os
import django
import math
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from django.utils import timezone
from queue_board.models import ClinicSetting, Patient, Token
from queue_board.utils import haversine

# Get clinic
clinic = ClinicSetting.objects.first()
print(f"Clinic Settings: Lat {clinic.latitude}, Lng {clinic.longitude}")

print("\n--- Testing Haversine Formula ---")
# Mock coordinates at 50 meters
lat_close, lng_close = 12.95350, 78.85045 # Adjusted very slightly
distance_close = haversine(clinic.latitude, clinic.longitude, lat_close, lng_close)
print(f"Mock 1 (Close): {distance_close:.2f} meters. Activation triggered if < 200m? {distance_close < 200}")

# Mock coordinates far away
lat_far, lng_far = 13.00000, 78.85045 # Adjusted far
distance_far = haversine(clinic.latitude, clinic.longitude, lat_far, lng_far)
print(f"Mock 2 (Far): {distance_far:.2f} meters. Activation triggered if < 200m? {distance_far < 200}")


print("\n--- Testing Token Expiration Logic ---")
patient, _ = Patient.objects.get_or_create(phone_number='+910000000001', defaults={'name': 'Test Expiration'})
token = Token.objects.filter(patient=patient).first()
if not token:
    token = Token.objects.create(patient=patient, token_number=999, status='INACTIVE')

# Backdate token generated_at by modifying directly via update since auto_now_add protects it usually
Token.objects.filter(id=token.id).update(generated_at=timezone.now() - timedelta(minutes=16), status='INACTIVE')
token.refresh_from_db()

print(f"Created inactive token ({token.id}). Emulating 16 minutes passage...")

# Now trigger the check that queue_status_api runs
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from queue_board.views import queue_status_api

request = RequestFactory().get('/api/status/')
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()
response = queue_status_api(request)

token.refresh_from_db()
print(f"Token status after background polling cleanup: {token.status}. Expired automatically? {token.status == 'CANCELLED'}")

print("\n--- Testing Queue Order / Priority & Wait Time ---")
patient2, _ = Patient.objects.get_or_create(phone_number='+910000000002', defaults={'name': 'Regular Patient'})
patient3, _ = Patient.objects.get_or_create(phone_number='+910000000003', defaults={'name': 'Priority Patient'})

tok2 = Token.objects.filter(patient=patient2).first()
if not tok2: tok2 = Token.objects.create(patient=patient2, token_number=1000, status='ACTIVE', is_priority=False)

tok3 = Token.objects.filter(patient=patient3).first()
if not tok3: tok3 = Token.objects.create(patient=patient3, token_number=1001, status='ACTIVE', is_priority=True)

active_tokens = Token.objects.filter(date=timezone.now().date(), status='ACTIVE')
print(f"Currently {active_tokens.count()} Active Tokens.")
for t in active_tokens:
    print(f"- #{t.token_number} {t.patient.name} (Priority: {t.is_priority}) | Expected Est. Wait: {t.get_estimated_wait_minutes()} mins")
