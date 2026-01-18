from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.utils import timezone
from django.contrib.auth import get_user_model

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} Profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Use get_or_create to prevent duplicates
        Profile.objects.get_or_create(user=instance)
        
        # Add to Customer group if not superuser
        if not instance.is_superuser:
            customer_group, _ = Group.objects.get_or_create(name='Customer')
            instance.groups.add(customer_group)

User = get_user_model()

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    purpose = models.CharField(max_length=50)  # e.g., 'registration', 'passenger_verification'
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def is_expired(self):
        """Check if OTP has expired (after 10 minutes)"""
        expiration_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiration_time
        
    class Meta:
        ordering = ['-created_at']
        
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BOOKING', 'Booking'),      # When coins are deducted for a booking
        ('CANCELLATION', 'Cancellation'),  # When coins are refunded for a cancellation
        ('ADD_COINS', 'Add Coins'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    travels = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_transactions')  # Reference to bus admin
    amount = models.PositiveIntegerField()  # The number of coins involved
    transaction_type = models.CharField(max_length=12, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)  # Optional description of the transaction

    class Meta:
        ordering = ['-timestamp']  # Newest transactions first

    def __str__(self):
        return f"Transaction b/w Customer : {self.user.username} and Admin : {self.travels.username if self.travels else 'Bookbus'} for {self.transaction_type} : Amount={self.amount}"