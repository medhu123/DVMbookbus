from django import forms
from django.db import models
from .models import Bus, Booking


class BusForm(forms.ModelForm):

    stops = forms.MultipleChoiceField(
        choices=Bus.Place.choices, 
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}), 
        required=False
    )

    class Meta:
        model = Bus
        fields = ['journey_start', 'stops', 'journey_end', 'start_time', 'end_time', 'total_seats', 'available_seats', 'fare']
        widgets = {
            'start_time': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }


    def clean_stops(self):
        stops = self.cleaned_data.get('stops', [])
        return stops



        

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