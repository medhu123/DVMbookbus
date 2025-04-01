from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from users.models import Profile

class Command(BaseCommand):
    help = 'Creates profiles for all existing users'

    def handle(self, *args, **options):
        # Ensure groups exist
        Group.objects.get_or_create(name='Customer')
        Group.objects.get_or_create(name='BusAdmin')
        
        for user in User.objects.all():
            # Create profile if doesn't exist
            Profile.objects.get_or_create(user=user)
            
            # Add to appropriate group
            if user.is_superuser:
                user.groups.add(Group.objects.get(name='BusAdmin'))
            else:
                user.groups.add(Group.objects.get(name='Customer'))
        
        self.stdout.write(self.style.SUCCESS('Successfully created profiles for all users'))