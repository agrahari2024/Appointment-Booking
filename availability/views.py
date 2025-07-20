from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import WeeklyAvailability, Booking
from .serializers import WeeklyAvailabilitySerializer, BookingSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

# Create your views here.

class WeeklyAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = WeeklyAvailability.objects.all()
    serializer_class = WeeklyAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Allow filtering by user
        user_id = self.request.query_params.get('user')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Validate booking slot
        booking = Booking(**serializer.validated_data)
        booking.clean()  # Will raise ValidationError if invalid
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        List available slots for a given user, weekday, and date.
        Query params: user, weekday, date, duration
        """
        user_id = request.query_params.get('user')
        weekday = request.query_params.get('weekday')
        date_str = request.query_params.get('date')
        duration = int(request.query_params.get('duration', 15))
        if not (user_id and weekday is not None and date_str):
            return Response({'detail': 'user, weekday, and date are required.'}, status=400)
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        availabilities = WeeklyAvailability.objects.filter(user_id=user_id, weekday=weekday)
        slots = []
        for avail in availabilities:
            start = datetime.combine(date, avail.start_time)
            end = datetime.combine(date, avail.end_time)
            # Get existing bookings for this slot
            bookings = Booking.objects.filter(availability=avail, date=date)
            booked_ranges = [(datetime.combine(date, b.start_time), datetime.combine(date, b.end_time)) for b in bookings]
            # Find free slots
            slot_start = start
            while slot_start + timedelta(minutes=duration) <= end:
                slot_end = slot_start + timedelta(minutes=duration)
                overlap = any(bs < slot_end and be > slot_start for bs, be in booked_ranges)
                if not overlap:
                    slots.append({
                        'availability_id': avail.id,
                        'start_time': slot_start.time(),
                        'end_time': slot_end.time(),
                        'duration': duration
                    })
                slot_start += timedelta(minutes=15)  # step by 15m
        return Response(slots)
