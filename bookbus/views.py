from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Bus, Booking, BusStop, Seat, Stop
from .forms import BookingSeatForm, FilterForm, BusForm, StopForm, BusStopForm
from django.db.models import F


def home(request):
    form = FilterForm(request.GET or None)
    buses = Bus.objects.all()

    if form.is_valid():
        journey_start = form.cleaned_data.get('journey_start')
        journey_end = form.cleaned_data.get('journey_end')

        if journey_start and journey_end:
            valid_buses = []
            for bus in buses:
                stops = list(bus.bus_stops.order_by("stop_order").values_list("stop__name", flat=True))
                if journey_start.name in stops and journey_end.name in stops:
                    if stops.index(journey_start.name) < stops.index(journey_end.name):
                        valid_buses.append(bus)
            buses = valid_buses
        elif journey_start:
            buses = buses.filter(bus_stops__stop=journey_start)
        elif journey_end:
            buses = buses.filter(bus_stops__stop=journey_end)

    stop_names = Stop.objects.values_list("name", flat=True).distinct()
    
    context = {
        'buses': buses,
        'form': form,
        'start_cities': stop_names,
        'end_cities': stop_names,
    }
    return render(request, 'bookbus/home.html', context)


class BusListView(ListView):
    model = Bus
    template_name = 'bookbus/home.html'
    context_object_name = 'buses'
    ordering = ['-start_time']
    paginate_by = 5


class UserBusListView(ListView):
    model = Bus
    template_name = 'bookbus/user_buses.html'
    ordering = ['-start_time']
    context_object_name = 'buses'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Bus.objects.filter(travels=user).order_by('-start_time')


class UserBookingListView(ListView):
    model = Booking
    template_name = 'bookbus/booked_buses.html'
    context_object_name = 'bookings'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return user.booking_set.all()


class BusDetailView(DetailView):
    model = Bus

class BusCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Bus
    form_class = BusForm
    template_name = 'bookbus/bus_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stop_form'] = BusStopForm()
        context['all_stops'] = Stop.objects.all()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.travels = self.request.user
        
        # Get stops from the form data
        stop_order = self.request.POST.get('stop_order', '').split(',')
        stop_order = [stop_id for stop_id in stop_order if stop_id]  # Filter empty strings
        
        # Validate at least 2 stops
        if len(stop_order) < 2:
            form.add_error(None, "Please select at least 2 stops")
            return self.form_invalid(form)
            
        try:
            # Set journey start/end from first and last stops
            self.object.journey_start = Stop.objects.get(id=stop_order[0])
            self.object.journey_end = Stop.objects.get(id=stop_order[-1])
            
            # Save the bus first
            self.object.save()
            
            # Create BusStop relationships
            for order, stop_id in enumerate(stop_order, start=1):
                BusStop.objects.create(
                    bus=self.object,
                    stop_id=stop_id,
                    stop_order=order
                )
                
            return redirect('bus-detail', pk=self.object.pk)
            
        except Stop.DoesNotExist:
            form.add_error(None, "One or more selected stops no longer exist")
            return self.form_invalid(form)
    
    def test_func(self):

        return self.request.user.groups.filter(name='BusAdmin').exists()


class BusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bus
    form_class = BusForm
    template_name = 'bookbus/bus_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_stops = self.object.bus_stops.order_by('stop_order')
        initial_stop_order = ','.join(str(bs.stop.id) for bs in current_stops)
        context['stop_form'] = BusStopForm(initial={'stop_order': initial_stop_order})
        context['all_stops'] = Stop.objects.all()
        context['current_stops'] = current_stops
        return context

    def form_valid(self, form):
        
        self.object = form.save()
        
        # Clear existing stops
        self.object.bus_stops.all().delete()
        
        # Add new stops
        stop_order = self.request.POST.get('stop_order', '').split(',')

        if len(stop_order) < 2:
            form.add_error(None, "Please select at least 2 stops")
            return self.form_invalid(form)
        


        try:
            # Set journey start/end from first and last stops
            self.object.journey_start = Stop.objects.get(id=stop_order[0])
            self.object.journey_end = Stop.objects.get(id=stop_order[-1])
            
            # Save the bus first
            self.object.save()
            
            # Create BusStop relationships
            for order, stop_id in enumerate(stop_order, start=1):
                BusStop.objects.create(
                    bus=self.object,
                    stop_id=stop_id,
                    stop_order=order
                )
                
            return redirect('bus-detail', pk=self.object.pk)
            
        except Stop.DoesNotExist:
            form.add_error(None, "One or more selected stops no longer exist")
            return self.form_invalid(form)
    

    def test_func(self):
        bus = self.get_object()
        return self.request.user == bus.travels

class BusDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bus
    success_url = '/'

    def test_func(self):
        bus = self.get_object()
        return self.request.user == bus.travels


def BusBookAddView(request, pk):
    """Handles booking a seat on a bus."""
    bus = get_object_or_404(Bus, pk=pk)

    if request.method == "POST":
        b_form = BookingSeatForm(request.POST)

        if b_form.is_valid():
            booking = b_form.save(commit=False)
            booking.user = request.user
            booking.bus = bus
            booking.save()

            # Update the seat count
            if booking.seat.seat_class == "General":
                Bus.objects.filter(pk=pk).update(general_seats=F('general_seats') - 1)
            elif booking.seat.seat_class == "Sleeper":
                Bus.objects.filter(pk=pk).update(sleeper_seats=F('sleeper_seats') - 1)
            elif booking.seat.seat_class == "Luxury":
                Bus.objects.filter(pk=pk).update(luxury_seats=F('luxury_seats') - 1)

            return redirect('booked-buses', request.user.username)

    else:
        b_form = BookingSeatForm()

    context = {
        'b_form': b_form,
        'bus': bus,
    }

    return render(request, 'bookbus/bus_book_add.html', context)


def BusBookRemoveView(request, pk):
    """Handles canceling a booking."""
    bus = get_object_or_404(Bus, pk=pk)
    booking = Booking.objects.filter(bus=bus, user=request.user).first()

    if request.method == "POST" and booking:
        seat_class = booking.seat.seat_class
        booking.delete()

        # Increase available seat count
        if seat_class == "General":
            Bus.objects.filter(pk=pk).update(general_seats=F('general_seats') + 1)
        elif seat_class == "Sleeper":
            Bus.objects.filter(pk=pk).update(sleeper_seats=F('sleeper_seats') + 1)
        elif seat_class == "Luxury":
            Bus.objects.filter(pk=pk).update(luxury_seats=F('luxury_seats') + 1)

        return redirect('booked-buses', request.user.username)

    return render(request, 'bookbus/bus_book_remove.html', {'bus': bus})

def add_stop(request):
    if request.method == "POST":
        form = StopForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bookbus-home')
    else:
        form = StopForm()
    
    return render(request, 'bookbus/add_stop.html', {'form': form})


def about(request):
    return render(request, 'bookbus/about.html', {'title': 'About'})