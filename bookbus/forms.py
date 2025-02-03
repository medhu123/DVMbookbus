from django import forms
from .models import Bus

class BusForm(forms.ModelForm):
    model = Bus
        fields = ['journey_start', 'journey_end', 'start_time', 'end_time', 'seats']
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }