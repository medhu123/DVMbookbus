from django.urls import path
from .views import home, BusListView, BusDetailView, BusCreateView, BusUpdateView, BusDeleteView, UserBusListView, BusBookAddView, BusBookRemoveView, UserBookingListView
from . import views as bus_views


urlpatterns = [
    path('', bus_views.home, name="bookbus-home"), #name added because we may need reverse lookup, which can't have common names like home because it may clash with other app integrations.
    path('user/<str:username>', UserBusListView.as_view(), name="user-buses"),
    path('user/<str:username>/bookings', UserBookingListView.as_view(), name="booked-buses"),
    path('bus/<int:pk>/', BusDetailView.as_view(), name="bus-detail"),
    path('bus/new/', BusCreateView.as_view(), name="bus-create"),
    path('bus/<int:pk>/update/', BusUpdateView.as_view(), name="bus-update"),
    path('bus/<int:pk>/delete/', BusDeleteView.as_view(), name="bus-delete"),
    path('bus/<int:pk>/book/add', bus_views.BusBookAddView, name="bus-book-add"),
    path('bus/<int:pk>/book/remove', bus_views.BusBookRemoveView, name="bus-book-remove"),
    path('add-stop/', bus_views.add_stop, name='add-stop'),
    path('about/',bus_views.about, name="bookbus-about")
]