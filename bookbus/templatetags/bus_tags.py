from django import template
from datetime import timedelta, datetime, date
from django.template.defaulttags import register

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dict(dictionary).get(int(key))

@register.filter
def time_since_previous_stop(bus_stop):
    try:
        # Get all stops for this bus route ordered by stop_order
        stops = bus_stop.bus.busstops.order_by('stop_order')
        # Find the current stop's position in the queryset
        stop_list = list(stops)
        current_index = stop_list.index(bus_stop)
        if current_index > 0:
            previous_stop = stop_list[current_index - 1]
            return calculate_time_difference(previous_stop, bus_stop)
    except (AttributeError, IndexError, ValueError):
        pass
    return ""

@register.filter
def time_until(first_stop, last_stop):
    return calculate_time_difference(first_stop, last_stop)

def calculate_time_difference(start_stop, end_stop):
    # Create datetime objects for comparison by combining with a dummy date
    dummy_date = date.today()
    start_time = datetime.combine(dummy_date, start_stop.arrival_time)
    end_time = datetime.combine(dummy_date, end_stop.arrival_time)
    
    # Calculate time difference considering next day
    if getattr(end_stop, 'is_next_day', False) and not getattr(start_stop, 'is_next_day', False):
        # Overnight trip - add 24 hours to the end time
        end_time += timedelta(days=1)
    
    time_diff = end_time - start_time
    
    # Handle negative time differences (shouldn't happen with proper stop ordering)
    if time_diff.days < 0:
        time_diff = timedelta(0)
    
    total_seconds = time_diff.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    parts = []
    if time_diff.days > 0:
        parts.append(f"{time_diff.days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "0m"

@register.filter
def add(date, days):
    return date + timedelta(days=days)