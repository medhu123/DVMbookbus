import random
import requests
from django.conf import settings
from django.utils import timezone
from .models import OTP

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email, purpose):
    """
    Send OTP email without user reference initially
    Returns the created OTP object
    """
    otp = generate_otp()
    otp_obj = OTP.objects.create(
        email=email,
        otp=otp,
        purpose=purpose,
        user=None  # Will be updated after verification
    )
    
    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET),
        json={
            "Messages": [{
                "From": {"Email": settings.MAILJET_SENDER_EMAIL, "Name": "BookBus"},
                "To": [{"Email": email}],
                "Subject": f"Your {purpose.replace('_', ' ').title()} OTP",
                "TextPart": f"Your OTP for verification is: {otp}",
            }]
        }
    )
    
    if response.status_code != 200:
        otp_obj.delete()  # Clean up if email fails
        raise Exception(f"Failed to send OTP: {response.text}")
    
    return otp_obj

def verify_otp(email, otp_code, purpose):
    """
    Verify OTP and return (success, message, otp_obj)
    """
    try:
        otp_obj = OTP.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=False
        ).latest('created_at')
        
        if otp_obj.is_expired():
            return False, "OTP has expired", None
            
        if otp_obj.otp == otp_code:
            otp_obj.is_verified = True
            otp_obj.save()
            return True, "OTP verified successfully", otp_obj
            
        return False, "Invalid OTP", None
        
    except OTP.DoesNotExist:
        return False, "OTP not found", None