from django.contrib import admin
from .models import Bus, Booking, Seat, Stop, BusStop

admin.site.register(Bus)
admin.site.register(Booking)
admin.site.register(Seat)
admin.site.register(Stop)
admin.site.register(BusStop)