from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Stop(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Bus(models.Model):

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    fare = models.IntegerField(default=0)

    general_seats = models.IntegerField(default=0)
    sleeper_seats = models.IntegerField(default=0)
    luxury_seats = models.IntegerField(default=0)

    travels = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    journey_start = models.ForeignKey(
        Stop, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='starting_buses'
    )
    journey_end = models.ForeignKey(
        Stop, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ending_buses'
    )

    def __str__(self):
        return f"Bus by {self.travels} from {self.journey_start} to {self.journey_end}"

    @property
    def stops_list(self):
        """Returns ordered list of stop names"""
        return [bus_stop.stop.name for bus_stop in self.bus_stops.order_by("stop_order")]

    @property
    def journey(self):
        return f"{self.journey_start}@{self.start_time} to {self.journey_end}@{self.end_time}"

    def get_absolute_url(self):
        return reverse('bus-detail', kwargs={'pk': self.pk})


class BusStop(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="bus_stops")
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_order = models.PositiveIntegerField()

    class Meta:
        unique_together = [("bus", "stop_order")]
        ordering = ["stop_order"]

    def __str__(self):
        return f"{self.bus} - {self.stop} (Order: {self.stop_order})"


class Seat(models.Model):
    SEAT_CLASSES = [
        ("General", "General"),
        ("Sleeper", "Sleeper"),
        ("Luxury", "Luxury"),
    ]

    name = models.CharField(max_length=10)  # Example: "S1", "S2"
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="seats")
    seat_class = models.CharField(max_length=10, choices=SEAT_CLASSES)

    class Meta:
        unique_together = ("bus", "name")  # Ensures seat names are unique per bus

    def __str__(self):
        return f"{self.name} - {self.seat_class} ({self.bus})"


class Booking(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)  
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)  
    start_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='booking_start')
    end_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='booking_end')
    date_booked = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bus', 'seat')  # Prevents double booking

    @classmethod
    def add_booking(cls, bus, customer, seat, start_stop, end_stop):
        """Prevents overlapping seat bookings."""
        overlapping_bookings = cls.objects.filter(
            bus=bus, seat=seat
        ).filter(
            models.Q(start_stop__stop_order__lt=end_stop.stop_order, end_stop__stop_order__gt=start_stop.stop_order)
        )

        if overlapping_bookings.exists():
            raise ValueError(f'Seat {seat} is already booked for this route segment!')

        return cls.objects.create(bus=bus, customer=customer, seat=seat, start_stop=start_stop, end_stop=end_stop)

    @classmethod
    def remove_booking(cls, bus, customer, seat):
        booking = cls.objects.filter(bus=bus, customer=customer, seat=seat).first()
        if booking:
            booking.delete()
        else:
            raise ValueError("Booking not found!")

    def __str__(self):
        return f'Booking: {self.customer} - {self.seat} on {self.bus} ({self.start_stop} → {self.end_stop})'