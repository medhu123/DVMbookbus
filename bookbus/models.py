from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class Stop(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Bus(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'), 
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    operating_days = models.JSONField(
        default=list,
        blank=True,
        help_text="List of days (0-6) the bus operates"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
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
    def is_recurring(self):
        return bool(self.operating_days)
    
    @property
    def general_seats(self):
        return self.seats.filter(seat_class="General").count()
    
    @property
    def sleeper_seats(self):
        return self.seats.filter(seat_class="Sleeper").count()
    
    @property
    def luxury_seats(self):
        return self.seats.filter(seat_class="Luxury").count()
    
    def runs_on_date(self, date):
        """Check if bus runs on specific date considering both recurring and date range"""
        date = date.date() if hasattr(date, 'date') else date
        weekday = date.weekday()
        
        # Check if date falls within bus schedule dates
        within_date_range = self.start_time.date() <= date <= self.end_time.date()
        
        # For recurring buses, check operating days OR date range
        if self.operating_days:
            return within_date_range and (weekday in self.operating_days)
        # For one-time buses, just check date range
        return within_date_range

    @property
    def runs_daily(self):
        return not bool(self.operating_days) 

    def get_day_display(self):
        return dict(self.DAY_CHOICES)

    @property
    def operating_days_display(self):
        day_names = []
        for day in self.operating_days:
            day_names.append(dict(self.DAY_CHOICES).get(day))
        return ", ".join(day_names)

    @property
    def stops_list(self):
        """Returns ordered list of stop names with times"""
        return [
            {
                'name': bus_stop.stop.name,
                'time': bus_stop.arrival_time.strftime('%H:%M'),
                'date': bus_stop.arrival_time.date()
            } 
            for bus_stop in self.bus_stops.order_by("stop_order")
        ]

    @property
    def journey(self):
        return f"{self.journey_start}@{self.start_time} to {self.journey_end}@{self.end_time}"

    def get_absolute_url(self):
        return reverse('bus-detail', kwargs={'pk': self.pk})


class BusStop(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="bus_stops")
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_order = models.PositiveIntegerField()
    arrival_time = models.TimeField(help_text="Time when bus arrives at this stop")
    is_next_day = models.BooleanField(default=False, 
                                    help_text="Check if arrival is next day (for overnight stops)")

    class Meta:
        unique_together = [("bus", "stop_order")]
        ordering = ["stop_order"]

    def __str__(self):
        return f"{self.bus} - {self.stop} (Order: {self.stop_order}, Time: {self.get_arrival_time_display()})"

    def get_arrival_time_display(self):
        time_str = self.arrival_time.strftime("%H:%M")
        return f"{time_str} (+1 day)" if self.is_next_day else time_str


class Seat(models.Model):
    SEAT_CLASSES = [
        ("General", "General"),
        ("Sleeper", "Sleeper"),
        ("Luxury", "Luxury"),
    ]

    name = models.CharField(max_length=10)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="seats")
    seat_class = models.CharField(max_length=10, choices=SEAT_CLASSES)
    fare = models.IntegerField(default=0)
    
    def get_status(self, travel_date):
        """Dynamic status based on bookings for the given date"""
        if self.bookings.filter(travel_date=travel_date).exists():
            return "Booked"
        return "Available"

    class Meta:
        unique_together = ("bus", "name")

    def __str__(self):
        return f"{self.bus} : {self.name} - {self.seat_class} (Rs.{self.fare})"

class Booking(models.Model):
    BOOKING_STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='bookings')
    start_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='booking_start')
    end_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='booking_end')
    date_booked = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField()
    status = models.CharField(max_length=10, choices=BOOKING_STATUS, default='Pending')
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_booked']  # Add this line
        unique_together = ('bus', 'seat', 'travel_date')

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

    def save(self, *args, **kwargs):
        # Convert travel_date to date object if it's a string
        if isinstance(self.travel_date, str):
            try:
                self.travel_date = datetime.datetime.strptime(self.travel_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass  # Handle invalid date format as needed
        
        # Update seat status based on booking status
        if self.status in ['Pending', 'Confirmed']:
            self.seat.status = 'Booked'
        elif self.status == 'Cancelled':
            self.seat.status = 'Available'
        self.seat.save()
        
        # Update status to Completed if travel date has passed
        if isinstance(self.travel_date, datetime.date) and self.travel_date < timezone.now().date() and self.status != 'Cancelled':
            self.status = 'Completed'
            
        super().save(*args, **kwargs)