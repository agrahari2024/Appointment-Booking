from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import WeeklyAvailability, Booking
from datetime import time, date

# Create your tests here.

class AvailabilityBookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.avail = WeeklyAvailability.objects.create(
            user=self.user, weekday=0, start_time=time(9,0), end_time=time(12,0)
        )

    def test_create_availability(self):
        resp = self.client.post('/api/availability/', {
            'user': self.user.id,
            'weekday': 1,
            'start_time': '13:00',
            'end_time': '15:00'
        })
        self.assertEqual(resp.status_code, 201)

    def test_overlap_availability(self):
        resp = self.client.post('/api/availability/', {
            'user': self.user.id,
            'weekday': 0,
            'start_time': '10:00',
            'end_time': '11:00'
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_booking(self):
        resp = self.client.post('/api/bookings/', {
            'availability': self.avail.id,
            'guest_name': 'Guest',
            'date': str(date.today()),
            'start_time': '09:00',
            'end_time': '09:30',
            'duration': 30
        })
        self.assertEqual(resp.status_code, 201)

    def test_overlap_booking(self):
        Booking.objects.create(
            availability=self.avail,
            guest_name='Guest1',
            date=date.today(),
            start_time=time(9,0),
            end_time=time(9,30),
            duration=30
        )
        resp = self.client.post('/api/bookings/', {
            'availability': self.avail.id,
            'guest_name': 'Guest2',
            'date': str(date.today()),
            'start_time': '09:15',
            'end_time': '09:45',
            'duration': 30
        })
        self.assertEqual(resp.status_code, 400)

    def test_available_slots(self):
        Booking.objects.create(
            availability=self.avail,
            guest_name='Guest1',
            date=date.today(),
            start_time=time(9,0),
            end_time=time(9,30),
            duration=30
        )
        resp = self.client.get(f'/api/bookings/available-slots/?user={self.user.id}&weekday=0&date={date.today()}&duration=30')
        self.assertEqual(resp.status_code, 200)
        slots = resp.json()
        for slot in slots:
            self.assertFalse(slot['start_time'] == '09:00')
