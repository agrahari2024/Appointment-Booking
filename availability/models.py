from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time, timedelta, datetime

class WeeklyAvailability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    WEEKDAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('user', 'weekday', 'start_time', 'end_time')
        ordering = ['user', 'weekday', 'start_time']

    def __str__(self):
        return f"{self.user.username} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Start time must be before end time.')
        # Prevent overlapping availabilities for the same user and weekday
        overlaps = WeeklyAvailability.objects.filter(
            user=self.user,
            weekday=self.weekday
        ).exclude(pk=self.pk)
        for avail in overlaps:
            if (self.start_time < avail.end_time and self.end_time > avail.start_time):
                raise ValidationError('Availability overlaps with another slot.')

class Booking(models.Model):
    availability = models.ForeignKey(WeeklyAvailability, on_delete=models.CASCADE, related_name='bookings')
    guest_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    duration = models.PositiveIntegerField(help_text='Duration in minutes')

    class Meta:
        unique_together = ('availability', 'date', 'start_time', 'end_time')
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.guest_name} booking on {self.date} {self.start_time}-{self.end_time}"

    def clean(self):
        # Ensure booking fits within the availability slot
        if self.start_time < self.availability.start_time or self.end_time > self.availability.end_time:
            raise ValidationError('Booking must fit within the available slot.')
        if self.start_time >= self.end_time:
            raise ValidationError('Booking start time must be before end time.')
        # Check duration matches
        expected_end = (datetime.combine(self.date, self.start_time) + timedelta(minutes=self.duration)).time()
        if expected_end != self.end_time:
            raise ValidationError('End time does not match duration.')
        # Prevent overlapping bookings
        overlaps = Booking.objects.filter(
            availability=self.availability,
            date=self.date
        ).exclude(pk=self.pk)
        for booking in overlaps:
            if (self.start_time < booking.end_time and self.end_time > booking.start_time):
                raise ValidationError('Booking overlaps with another booking.')
