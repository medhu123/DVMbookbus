from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    coins = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name='Customer'))