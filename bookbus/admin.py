from django.contrib import admin
from .models import Bus, Booking, Seat, Stop, BusStop

admin.site.register(Bus)
admin.site.register(Stop)
admin.site.register(BusStop)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('passenger_name', 'bus', 'seat', 'travel_date', 'status')
    list_filter = ('status', 'travel_date', 'bus')
    search_fields = ('passenger_name', 'passenger_email', 'bus__name')
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')
    mark_completed.short_description = "Mark selected bookings as Completed"

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('name', 'bus', 'seat_class', 'fare', 'current_status')
    
    def current_status(self, obj):
        # Implement similar to your get_status method
        return "Dynamic Status"  # Replace with actual implementation
    current_status.short_description = 'Status'