from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Bus(models.Model):

    class Place(models.TextChoices):
        DEL = 'Delhi'
        JAI = 'Jaipur'
        PIL = 'Pilani'
        KOT = 'Kota'
        JOD = 'Jodhpur'
        UDA = 'Udaipur'

    journey_start = models.CharField(
        max_length=20,
        choices=Place.choices,
        default=Place.PIL
    )

    journey_end = models.CharField(
        max_length=20,
        choices=Place.choices,
        default=Place.DEL
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def journey(self):
        return f"{self.journey_start}@{self.start_time} to {self.journey_end}@{self.end_time}"

    fare = models.IntegerField(default = 0)
    total_seats = models.IntegerField(default = 0)
    available_seats = models.IntegerField(default = 0)

    date_added = models.DateTimeField(default=timezone.now)

    travels = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.journey_start} to {self.journey_end} by {self.travels}'

    def get_absolute_url(self):
        return reverse('bus-detail', kwargs={'pk':self.pk})


class Booking(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    customers = models.ManyToManyField(User)
    seats_booked = models.IntegerField(default = 0)

    @classmethod
    def add_booking(cls, bus, new_customer):
        booking, created = cls.objects.get_or_create(bus=bus)
        booking.customers.add(new_customer)
    
    @classmethod
    def remove_booking(cls, bus, customer):
        booking, created = cls.objects.get_or_create(bus=bus)
        booking.customers.remove(customer)
    
    def __str__(self):
        return f'{self.bus} booked by {list(self.customers.all())}'