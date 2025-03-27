from django import forms
from django.db import models
from .models import Bus, Booking, BusStop, Seat, Stop


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['start_time', 'end_time', 'fare', 'general_seats', 'sleeper_seats', 'luxury_seats']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BusStopForm(forms.Form):
    stops = forms.ModelMultipleChoiceField(
        queryset=Stop.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    stop_order = forms.CharField(widget=forms.HiddenInput())



class BookingSeatForm(forms.ModelForm):
    seat = forms.ModelChoiceField(queryset=Seat.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Booking
        fields = ['seat', 'start_stop', 'end_stop']

    def __init__(self, *args, **kwargs):
        bus = kwargs.pop('bus', None)
        super().__init__(*args, **kwargs)
        if bus:
            self.fields['seat'].queryset = Seat.objects.filter(bus=bus)
            self.fields['start_stop'].queryset = bus.bus_stops.all().order_by('stop_order')
            self.fields['end_stop'].queryset = bus.bus_stops.all().order_by('stop_order')

class FilterForm(forms.Form):
    journey_start = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        required=False,
        label="Starting Stop",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    journey_end = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        required=False,
        label="Destination Stop",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        fields = ['journey_start', 'journey_end']

class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stop name'})
        }