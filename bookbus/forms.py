from django import forms
from django.db import models
from .models import Bus, Booking, BusStop, Seat, Stop
from django.db.models import Q, F
import datetime

class SeatSelectionForm(forms.Form):
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'travel-date-input'
        }),
        label="Travel Date"
    )

    def __init__(self, *args, bus=None, **kwargs):
        initial = kwargs.get('initial', {})
        super().__init__(*args, **kwargs)
        self.bus = bus
        if bus:
            today = datetime.date.today()
            self.fields['travel_date'].widget.attrs.update({
                'min': today.strftime('%Y-%m-%d'),
                'max': bus.end_time.date().strftime('%Y-%m-%d')
            })
            if 'travel_date' in initial:
                try:
                    self.fields['travel_date'].initial = datetime.datetime.strptime(
                        initial['travel_date'], '%Y-%m-%d'
                    ).date()
                except (ValueError, TypeError):
                    pass

    def clean_travel_date(self):
        travel_date = self.cleaned_data['travel_date']
        if not self.bus:
            raise ValidationError("Invalid bus selection")
        
        if travel_date < datetime.date.today():
            raise ValidationError("Travel date cannot be in the past")
        
        if not self.bus.runs_on_date(travel_date):
            raise ValidationError("Bus doesn't operate on selected date")
        
        return travel_date

    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        
        if not travel_date:
            return cleaned_data
            
        selected_seats = []
        for field_name, value in self.data.items():
            if field_name.startswith('seat_') and value == 'on':
                seat_id = field_name.split('_')[1]
                try:
                    seat = Seat.objects.get(id=seat_id, bus=self.bus)
                    selected_seats.append(seat)
                except Seat.DoesNotExist:
                    continue
        
        if not selected_seats:
            raise ValidationError("Please select at least one seat")
        
        booked_seats = Booking.objects.filter(
            seat__in=selected_seats,
            travel_date=travel_date
        ).select_related('seat')
        
        if booked_seats.exists():
            booked_names = [bs.seat.name for bs in booked_seats]
            raise ValidationError(
                f"These seats are already booked: {', '.join(booked_names)}"
            )
        
        cleaned_data['selected_seats'] = selected_seats
        return cleaned_data

class PassengerInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        seat_count = kwargs.pop('seat_count', 1)
        bus = kwargs.pop('bus', None)
        super().__init__(*args, **kwargs)
        
        self.fields['start_stop'] = forms.ModelChoiceField(
            queryset=BusStop.objects.none(),
            label="Boarding Stop",
            required=True
        )
        self.fields['end_stop'] = forms.ModelChoiceField(
            queryset=BusStop.objects.none(),
            label="Destination Stop",
            required=True
        )
        
        if bus:
            stops = bus.bus_stops.all().order_by('stop_order')
            self.fields['start_stop'].queryset = stops
            self.fields['end_stop'].queryset = stops
        
        for i in range(seat_count):
            self.fields[f'passenger_name_{i}'] = forms.CharField(
                label=f'Passenger {i+1} Name',
                max_length=100,
                required=True
            )
            self.fields[f'passenger_email_{i}'] = forms.EmailField(
                label=f'Passenger {i+1} Email',
                required=True
            )

    def get_passenger_fields(self):
        passengers = []
        i = 0
        while f'passenger_name_{i}' in self.fields:
            passengers.append((
                self[f'passenger_name_{i}'],
                self[f'passenger_email_{i}']
            ))
            i += 1
        return passengers

class BusForm(forms.ModelForm):
    operating_days = forms.MultipleChoiceField(
        choices=Bus.DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Operating Days"
    )

    # Seat configuration fields
    general_count = forms.IntegerField(min_value=0, initial=0, label="General Seats")
    sleeper_count = forms.IntegerField(min_value=0, initial=0, label="Sleeper Seats")
    luxury_count = forms.IntegerField(min_value=0, initial=0, label="Luxury Seats")
    
    general_fare = forms.IntegerField(min_value=0, initial=0, label="General Fare")
    sleeper_fare = forms.IntegerField(min_value=0, initial=0, label="Sleeper Fare")
    luxury_fare = forms.IntegerField(min_value=0, initial=0, label="Luxury Fare")

    class Meta:
        model = Bus
        fields = [
            'start_time', 'end_time', 'operating_days'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.operating_days:
            self.initial['operating_days'] = [str(day) for day in self.instance.operating_days]
        
        if self.instance.pk:
            seats = self.instance.seats.all()
            self.initial.update({
                'general_count': seats.filter(seat_class="General").count(),
                'sleeper_count': seats.filter(seat_class="Sleeper").count(),
                'luxury_count': seats.filter(seat_class="Luxury").count(),
            })
            
            if seats.exists():
                self.initial.update({
                    'general_fare': seats.filter(seat_class="General").first().fare if seats.filter(seat_class="General").exists() else 0,
                    'sleeper_fare': seats.filter(seat_class="Sleeper").first().fare if seats.filter(seat_class="Sleeper").exists() else 0,
                    'luxury_fare': seats.filter(seat_class="Luxury").first().fare if seats.filter(seat_class="Luxury").exists() else 0,
                })


    def clean_operating_days(self):
        data = self.cleaned_data.get('operating_days', [])
        # Convert selected days to integers
        return [int(day) for day in data] if data else []

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save operating_days as JSON list
        instance.operating_days = self.cleaned_data['operating_days']
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class BusStopForm(forms.Form):
    stops = forms.ModelMultipleChoiceField(
        queryset=Stop.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    stop_order = forms.CharField(widget=forms.HiddenInput())
    stop_times = forms.CharField(widget=forms.HiddenInput())
    next_day_flags = forms.CharField(widget=forms.HiddenInput())

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

    travel_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': datetime.date.today().strftime('%Y-%m-%d')
        }),
        label="Travel Date"
    )

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
        fields = ['journey_start', 'journey_end', 'travel_date']


class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stop name'})
        }