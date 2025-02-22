from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Bus, Booking
from .forms import BookingSeatForm, FilterForm, BusForm
from django.http import HttpResponse
from django.db import models


def home(request):

    journey_start = request.GET.get("journey_start", "")
    journey_end = request.GET.get("journey_end", "")
    buses = Bus.objects.all()

    cities = Bus.objects.values_list("stops", flat=True).distinct()
    city = list(set([item for sublist in cities for item in sublist]))  # Flatten list

    start_cities = list(set(Bus.objects.values_list("journey_start", flat=True).distinct()))
    end_cities = list(set(Bus.objects.values_list("journey_end", flat=True).distinct()))

    city.extend(start_cities + end_cities)
    city = list(set(city)) 

    if journey_start and journey_end:
        valid_buses = []

        for bus in buses:

            stops = [bus.journey_start] + bus.stops + [bus.journey_end]

            if journey_start in stops and journey_end in stops:
                if stops.index(journey_start) < stops.index(journey_end):
                    valid_buses.append(bus)

        buses = valid_buses
        print("Final filtered buses:", buses)


    elif journey_start:
        start_filter = []
        for bus in buses:
            stops = bus.stops

            if journey_start in stops or journey_start == bus.journey_start:
                start_filter.append(bus)

        buses = start_filter

    elif journey_end:
        end_filter = []
        for bus in buses:
            stops = bus.stops

            if journey_end in stops or journey_end == bus.journey_end:
                end_filter.append(bus)

        buses = end_filter


    context = {
            'buses': buses,
            'bookings':Booking.objects.all(),
            "start_cities": city,
            "end_cities": city,
    } 

    return render(request, 'bookbus/home.html', context)

class BusListView(ListView):

    model = Bus
    template_name='bookbus/home.html'
    context_object_name = 'buses'
    ordering = ['-start_time']
    paginate_by = 5


class UserBusListView(ListView):
    model = Bus
    template_name='bookbus/user_buses.html'
    ordering = ['-start_time']
    context_object_name = 'buses'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Bus.objects.filter(travels=user).order_by('-start_time')

class UserBookingListView(ListView):
    model = Booking
    template_name='bookbus/booked_buses.html'
    context_object_name = 'bookings'
    paginate_by = 5

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs.get('username')).first().booking_set.all()


class BusDetailView(DetailView):
    model = Bus


class BusCreateView(LoginRequiredMixin, UserPassesTestMixin,CreateView):
    model = Bus
    form_class = BusForm
    template_name = 'bookbus/bus_form.html'

    """def get_initial(self):
        initial = super().get_initial()
        bus = self.get_object()
        initial['stops'] = bus.stops
        return initial"""

    def form_valid(self, form):
        form.instance.travels = self.request.user
        form.instance.stops = form.cleaned_data['stops']
        return super().form_valid(form)

    def test_func(self):

        return self.request.user.groups.filter(name='BusAdmin').exists()


class BusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    
    model = Bus
    form_class = BusForm
    template_name = 'bookbus/bus_form.html'

    def get_initial(self):
        initial = super().get_initial()
        bus = self.get_object()
        initial['stops'] = bus.stops
        return initial

    def form_valid(self, form):
        form.instance.travels = self.request.user
        form.instance.stops = form.cleaned_data['stops']
        return super().form_valid(form)

    """def get_success_url(self):
        return reverse('bus_detail', kwargs={'pk': self.object.pk})"""
    
    def test_func(self):
        bus = self.get_object()
        return self.request.user == bus.travels


class BusDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bus
    success_url='/'
    
    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.travels:
            return True
        
        return False

def BusBookAddView(request, pk):
    model = Booking


    if request.method=="POST":
        bus = Bus.objects.filter(pk=pk)
        b_form = BookingSeatForm(request.POST, instance = bus.first().booking_set.first())

        if b_form.is_valid():
            booking = b_form.save(commit=False)
            booking.bus_id = bus.first().id
            booking.save()
            Booking.add_booking(Bus.objects.filter(pk=pk).first(),request.user)
            bus.update(available_seats=models.F('total_seats') - bus.first().booking_set.first().seats_booked)
            return redirect('booked-buses', request.user.username)
    
    else:
        bus = Bus.objects.filter(pk=pk)
        b_form = BookingSeatForm(request.POST, instance = bus.first().booking_set.first())
    
    context = {
        'b_form': b_form,
    }

    return render(request, 'bookbus/bus_book_add.html', context)

def BusBookRemoveView(request, pk):
    model = Booking

    if request.method=="POST":
        bus = Bus.objects.filter(pk=pk)
        Booking.remove_booking(Bus.objects.filter(pk=pk).first(),request.user)
        Bus.objects.filter(pk=pk).update(available_seats=models.F('available_seats') + bus.first().booking_set.first().seats_booked)
        return redirect('booked-buses', request.user)
        

    return render(request, 'bookbus/bus_book_remove.html')


def about(request):
    return render(request, 'bookbus/about.html', {'title':'About'})

    
