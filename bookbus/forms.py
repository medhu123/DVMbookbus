from django import forms
from django.db import models
from .models import Bus, Booking


class BusForm(forms.ModelForm):
    model = Bus
    fields = ['journey_start', 'journey_end', 'start_time', 'end_time', 'total_seats', 'available_seats', 'fare']
    widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
    }

        

class BookingSeatForm(forms.ModelForm):
    seats_booked = forms.IntegerField()
    class Meta:
        model = Booking
        fields = ['seats_booked']

class FilterForm(forms.ModelForm):

    """class Place(models.TextChoices):
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
    )"""


    class Meta:

        model = Bus
        fields = ['journey_start', 'journey_end']