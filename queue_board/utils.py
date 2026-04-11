import math
from twilio.rest import Client
from django.conf import settings

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    
    distance_km = c * r
    return distance_km * 1000 # returns in meters

def send_queue_sms(to_number, message):
    """ Sends an SMS using Twilio. Fails silently if settings are missing. """
    try:
        sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

        if not all([sid, token, from_number]) or not to_number:
            print("Twilio settings missing or no phone number provided.")
            return False

        # Ensure to_number has a country code (assuming +91 for India as per previous context/location)
        if to_number and not to_number.startswith('+'):
            to_number = f'+91{to_number}'

        client = Client(sid, token)
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False
