from rest_framework import serializers
from .models import WeeklyAvailability, Booking

class WeeklyAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyAvailability
        fields = ['id', 'user', 'weekday', 'start_time', 'end_time']
        read_only_fields = ['id']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'availability', 'guest_name', 'date', 'start_time', 'end_time', 'duration']
        read_only_fields = ['id'] 