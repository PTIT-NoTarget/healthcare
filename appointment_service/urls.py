from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, TimeslotAvailabilityView

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('timeslots/available/', TimeslotAvailabilityView.as_view(), name='timeslot-availability'),

]

