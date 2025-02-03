from django.urls import path
from .views import BusListView, BusDetailView, BusCreateView, BusUpdateView, BusDeleteView, UserBusListView
from . import views


urlpatterns = [
    path('', BusListView.as_view(), name="bookbus-home"), #name added because we may need reverse lookup, which can't have common names like home because it may clash with other app integrations.
    path('user/<str:username>', UserBusListView.as_view(), name="user-buses"),
    path('bus/<int:pk>/', BusDetailView.as_view(), name="bus-detail"),
    path('bus/new/', BusCreateView.as_view(), name="bus-create"),
    path('bus/<int:pk>/update/', BusUpdateView.as_view(), name="bus-update"),
    path('bus/<int:pk>/delete/', BusDeleteView.as_view(), name="bus-delete"),
    path('about/',views.about, name="bookbus-about")


]