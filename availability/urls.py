from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import WeeklyAvailabilityViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'availability', WeeklyAvailabilityViewSet, basename='availability')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('bookings/available-slots/', BookingViewSet.as_view({'get': 'available_slots'}), name='available-slots'),
] 