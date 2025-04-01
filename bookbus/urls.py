from django.urls import path
from . import views as bus_views


urlpatterns = [
    path('', bus_views.home, name="bookbus-home"), #name added because we may need reverse lookup, which can't have common names like home because it may clash with other app integrations.
    path('user/<str:username>', bus_views.UserBusListView.as_view(), name="user-buses"),
    path('user/<str:username>/bookings', bus_views.UserBookingListView.as_view(), name="booked-buses"),
    path('bus/<int:pk>/', bus_views.BusDetailView.as_view(), name="bus-detail"),
    path('bus/new/', bus_views.BusCreateView.as_view(), name="bus-create"),
    path('bus/<int:pk>/update/', bus_views.BusUpdateView.as_view(), name="bus-update"),
    path('bus/<int:pk>/delete/', bus_views.BusDeleteView.as_view(), name="bus-delete"),
    path('add-stop/', bus_views.add_stop, name='add-stop'),
    path('bus/<int:pk>/book/', bus_views.bus_book, name='bus-book'),
    path('bus/<int:pk>/passenger-info/', bus_views.passenger_info, name='passenger-info'),
    path('booking/<int:pk>/cancel/', bus_views.cancel_booking, name='cancel-booking'),
    path('export/', bus_views.ExportBookingsView.as_view(), name='export-view'),
    path('export/excel/', bus_views.ExportBookingsExcelView.as_view(), name='export-excel'),
    path('about/',bus_views.about, name="bookbus-about")
]