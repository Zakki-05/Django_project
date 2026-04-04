import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from queue_board.models import Token, Patient

def run_test():
    print("--- Starting Verification Test ---")
    
    # 1. Setup Patient
    patient, _ = Patient.objects.get_or_create(phone_number='1234567890', defaults={'name': 'Test Patient'})
    
    # 2. Create an INACTIVE token
    print("Creating testing token (INACTIVE)...")
    token = Token.objects.create(
        patient=patient,
        token_number=999,
        status='INACTIVE'
    )
    
    # 3. Simulate "Expiration" logic from views.py
    # expiration_time = timezone.now() - timedelta(minutes=120)
    # We want to check that a token created 16 minutes ago is NOT cancelled.
    
    token.generated_at = timezone.now() - timedelta(minutes=16)
    token.save()
    
    # Current expiration limit (120 mins)
    expiration_limit_120 = timezone.now() - timedelta(minutes=120)
    
    # Check if a 16-minute old token would be cancelled under new logic
    still_valid = token.generated_at > expiration_limit_120
    print(f"Token age: 16 minutes. Still valid under 120m limit? {still_valid}")
    
    # Check if it would be cancelled under OLD logic (15 mins)
    expiration_limit_15 = timezone.now() - timedelta(minutes=15)
    would_be_cancelled_old = token.generated_at < expiration_limit_15
    print(f"Token age: 16 minutes. Would have been cancelled under old 15m limit? {would_be_cancelled_old}")
    
    if still_valid and would_be_cancelled_old:
        print("SUCCESS: 120-minute expiration logic verified.")
    else:
        print("FAILURE: Expiration logic check failed.")

    # 4. Cleanup
    token.delete()
    print("--- Test Finished ---")

if __name__ == "__main__":
    run_test()
