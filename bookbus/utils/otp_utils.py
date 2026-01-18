import random
import requests
from django.conf import settings
from bookbus.models import PassengerOTP

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, booking=None):
    otp = generate_otp()
    PassengerOTP.objects.create(email=email, otp=otp, booking=booking)
    
    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET),
        json={
            "Messages": [
                {
                    "From": {
                        "Email": settings.MAILJET_SENDER_EMAIL,
                        "Name": "BookBus"
                    },
                    "To": [
                        {
                            "Email": email,
                        }
                    ],
                    "Subject": "Your Booking OTP Verification",
                    "TextPart": f"Your OTP for booking verification is: {otp}",
                }
            ]
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to send OTP: {response.text}")

def verify_otp(email, otp_code):
    try:
        otp_obj = PassengerOTP.objects.filter(
            email=email,
            is_verified=False
        ).latest('created_at')
        
        if otp_obj.otp == otp_code:
            otp_obj.is_verified = True
            otp_obj.save()
            return True
        return False
    except PassengerOTP.DoesNotExist:
        return False