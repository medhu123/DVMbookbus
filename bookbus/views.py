from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Bus, Booking
from django.http import HttpResponse




def home(request):
   context = {
        'buses': Bus.objects.all(),
        'bookings':Booking.objects.all()
   } 
   return render(request, 'blog/home.html', context)

class BusListView(ListView):
    model = Bus
    template_name='bookbus/home.html'
    context_object_name = 'buses'
    ordering = ['-date_added']
    paginate_by = 5

class UserBusListView(ListView):
    model = Bus
    template_name='bookbus/user_buses.html'
    context_object_name = 'buses'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Bus.objects.filter(travels=user).order_by('-date_added')

class UserBookingListView(ListView):
    model = Booking
    template_name='bookbus/booked_buses.html'
    context_object_name = 'bookings'
    paginate_by = 5

    """def get_queryset(self):
        return User.objects.filter(username=self.kwargs.get('username')).first().booking_set.all()"""


class BusDetailView(DetailView):
    model = Bus


class BusCreateView(LoginRequiredMixin, UserPassesTestMixin,CreateView):
    model = Bus
    fields = ['journey_start','journey_end', 'start_time', 'end_time','total_seats', 'available_seats']#'total_seats', 'available_seats']

    def form_valid(self, form):
        form.instance.travels = self.request.user
        """if form.instance.total_seats<form.instance.available_seats:
            return False"""
        return super().form_valid(form)

    def test_func(self):

        return self.request.user.groups.filter(name='BusAdmin').exists()


class BusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bus
    fields = ['journey_start','journey_end', 'start_time', 'end_time','total_seats', 'available_seats']#'total_seats', 'available_seats']

    def form_valid(self, form):
        form.instance.travels = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.travels:
            return True
        
        return False

class BusDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bus
    success_url='/'
    
    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.travels:
            return True
        
        return False

def BusBookAddView(request, pk):
    model = Bus

    if request.method=="POST":
        Booking.add_booking(Bus.objects.filter(pk=pk).first(),request.user)
        return redirect('/')


    return render(request, 'bookbus/bus_book_add.html')


def about(request):
    return render(request, 'bookbus/about.html', {'title':'About'})

    
