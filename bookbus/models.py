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
        default=Place.PIL
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    def journey(self):
        return f"{self.journey_start}@{self.start_time} to {self.journey_end}@{self.end_time}"

    total_seats = models.IntegerField(default = 0)
    available_seats = models.IntegerField(default = 0)

    #available_seats = models.IntegerField()

    date_added = models.DateTimeField(default=timezone.now)

    travels = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.journey_start} to {self.journey_end} by {self.travels}'

    def get_absolute_url(self):
        return reverse('bus-detail', kwargs={'pk':self.pk})