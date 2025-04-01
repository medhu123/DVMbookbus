from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


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