# management/commands/update_completed_bookings.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bookbus.models import Booking

class Command(BaseCommand):
    help = 'Updates booking status to Completed for past travel dates'

    def handle(self, *args, **options):
        today = timezone.now().date()
        updated = Booking.objects.filter(
            travel_date__lt=today,
            status__in=['Pending', 'Confirmed']
        ).update(status='Completed')
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} bookings to Completed status'))